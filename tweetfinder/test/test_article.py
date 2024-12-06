import os
from unittest import TestCase
import logging
import time
from goose3 import Goose
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from tweetfinder import Article

this_dir = os.path.dirname(os.path.abspath(__file__))
fixtures_dir = os.path.join(this_dir, "fixtures")

logging.getLogger('readability.readability').setLevel(logging.DEBUG)

'''
This utilizes a few webpages as static test cases:
 * [guardian](https://www.theguardian.com/world/2021/may/13/how-covid-lockdown-forged-unlikely-friendships)
 * [npr](https://www.npr.org/sections/health-shots/2021/05/18/997461471/its-time-for-americas-fixation-with-herd-immunity-to-end-scientists-say) 
 * [cnn](https://www.cnn.com/us/live-news/san-jose-ca-shooting-05-26-21/h_41658163e6c6f2416d346adb6c01119f)
 * [time](https://time.com/4263227/most-popular-tweets/)
'''


def _load_fixture(filename: str, return_article: bool = True) -> Article|str:
    """
    Load a single story from a local HTML file and parse it into an Article
    :param filename:
    :param return_article:
    :return:
    """
    # If the article has a link to a twitter account that should not return as an embed
    with open(os.path.join(fixtures_dir, filename)) as f:
        article_html = f.read()
    if return_article:
        article = Article(html=article_html)
        return article
    return article_html


class TestEmbeddedTweets(TestCase):
    """
    Test our parsing of embedded tweets, and compare to other libraries
    """

    def testOneGooseMisses(self):
        # make sure we catch ones Goose misses (this article has one embedded)
        g = Goose()
        goose_article = g.extract(raw_html=_load_fixture("cnn.html", False))
        goose_tweets = goose_article.tweets
        assert len(goose_tweets) == 0
        article = _load_fixture("cnn.html")
        assert article.count_embedded_tweets() == 1

    def testLinkNoEmbeds(self):
        # make sure a link to twitter in the HTML doesn't cound as an embedded tweet
        article = _load_fixture("1987377089.html")
        assert article.count_mentioned_tweets() == 0
        assert article.count_embedded_tweets() == 0

    def testMultipleEmbeds(self):
        article = _load_fixture("time.html")
        assert article.embeds_tweets() is True
        assert article.count_embedded_tweets() == 11
        tweets = article.list_embedded_tweets()
        assert tweets[1]['tweet_id'] == "580932146874957824"

    def testNoEmbeds(self):
        article = _load_fixture("npr.html")
        assert article.embeds_tweets() is False
        assert article.count_embedded_tweets() == 0
        article = _load_fixture("guardian.html")
        assert article.embeds_tweets() is False
        assert article.count_embedded_tweets() == 0


class TestMentionedTweets(TestCase):
    """
    Test our parsing of mentioned of tweets or Twitter, and support for customizing
    """

    def testMultipleMentionsAndNoEmbeds(self):
        article = _load_fixture("guardian.html")
        assert article.mentions_tweets() is True
        assert article.embeds_tweets() is False
        mentions = article.list_mentioned_tweets()
        assert len(mentions) == article.count_mentioned_tweets()
        assert len(mentions) == 2
        print("!!!!"+mentions[0]['phrase'])
        assert mentions[0]['phrase'] == "from a tweet"
        assert "virtually with friends I made from a tweet".lower() in mentions[0]['context']
        assert mentions[1]['phrase'] == "tweeted"
        assert "randomly tweeted something" in mentions[1]['context']

    def testMentionInLinkNotText(self):
        # this article has a mention in a link - "tweets" - not in text so that shouldn't count
        article = Article("https://www.theguardian.com/film/2020/jan/01/the-most-exciting-movies-of-2020-horror")
        assert article.mentions_tweets() is False

    def testNoMentions(self):
        article = _load_fixture("npr.html")
        assert article.mentions_tweets() is False
        assert article.count_mentioned_tweets() == 0


class TestParsing(TestCase):
    """
    Test basic parsing and fetching of webpages
    """

    def testBadIntialization(self):
        try:
            _ = Article()
            assert False
        except ValueError:
            assert True

    def testGetContent(self):
        article = _load_fixture("npr.html")
        content = article.get_content()
        assert content.startswith('<html><body><div>')
        assert 'storytext' in content[:100]

    def testGetHtml(self):
        article = _load_fixture("npr.html")
        html = article.get_html()
        assert html.startswith('<!doctype html>')


class TestArticleViaSelenium(TestCase):
    """
    Test, and provide an example, of how to use Selenium to parse HTML rendered by a JS-heaving webpage. 
    """

    def setUp(self):
        # setup a headless chrome we can re-use it in all the tests within this class
        chrome_options = Options()
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--headless')
        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def _loadViaSelenium(self, url: str, delay_secs: int = 1):
        self.driver.get(url)
        # let it render the javscript, then grab the *rendered* html, not the source_html
        time.sleep(delay_secs)  # hopefully it renders after this much time
        html_element = self.driver.find_element(By.TAG_NAME, 'html')
        rendered_html = html_element.get_attribute('innerHTML')
        # now that we have HTML rendered by Javascript, we can check for tweets
        return Article(html=rendered_html)

    def testSeleniumLoad(self):
        # this URL has 3 embedded tweets that are added by Javascript
        url = "https://www.foxnews.com/politics/black-lives-matter-hamas-terrorists-israeli"
        article = self._loadViaSelenium(url)
        assert article.count_embedded_tweets() == 3

    '''
    # This tests against our manually coded set of articles. However, since it loads those live this isn't a great
    # unit test - the media compaines change their code and probably the URLs will 404 soon. So I'm removing this
    # unit test but leaving the code here as an example for how to run against a set of articles.  
    def testHandCodedList(self):
        tweet_embed_data = pd.read_csv(os.path.join(fixtures_dir, '2021-manual-stories.csv'))
        for _, row in tweet_embed_data.iterrows():
            if row['embedded_via_js'] == 1:
                article = self._loadViaSelenium(row['url'])
            else:
                article = Article(row['url'])
            calculated_tweet_count = article.count_embedded_tweets()
            true_tweet_count = row['tweet_count']
            assert calculated_tweet_count == true_tweet_count
    '''