import os
from unittest import TestCase

from tweetfinder import Article

this_dir = os.path.dirname(os.path.abspath(__file__))
fixtures_dir = os.path.join(this_dir, "fixtures")


'''
This utilizes a few webpages as static test cases:
 * [fox-business](https://www.foxbusiness.com/lifestyle/gas-prices-increasing-midwest-memorial-day-weekend)
 * [guardian](https://www.theguardian.com/world/2021/may/13/how-covid-lockdown-forged-unlikely-friendships)
 * [npr](https://www.npr.org/sections/health-shots/2021/05/18/997461471/its-time-for-americas-fixation-with-herd-immunity-to-end-scientists-say) 
'''


def _load_fixture(filename):
    # If the article has a link to a twitter account that should not return as an embed
    with open(os.path.join(fixtures_dir, filename)) as f:
        article_html = f.read()
    article = Article(html=article_html)
    return article


class TestEmbeddedTweets(TestCase):

    def testLinkNoEmbeds(self):
        # make sure a link to twitter in the HTML doesn't cound as an embedded tweet
        article = _load_fixture("1987377089.html")
        assert article.count_mentioned_tweets() == 0
        assert article.count_embedded_tweets() == 0

    def testMultipleEmbeds(self):
        article = _load_fixture("fox-business.html")
        # make sure some embedded tweets were detected at all
        assert article.embeds_tweets() is True
        # make sure the number of embedded tweets is right
        embeds = article.list_embedded_tweets()
        assert len(embeds) == 4
        assert len(embeds) == article.count_embedded_tweets()
        # make sure the usernames whose tweets are embedded are correct
        embedded_usernames = set([t['username'] for t in embeds])
        assert len(embedded_usernames) == 2
        assert embedded_usernames[0] == 'GasBuddyGuy'
        assert embedded_usernames[1] == 'AAA_Travel'

    def testNoEmbeds(self):
        article = _load_fixture("npr.html")
        assert article.embeds_tweets() is False
        assert article.count_embedded_tweets() == 0
        article = _load_fixture("guardian.html")
        assert article.embeds_tweets() is False
        assert article.count_embedded_tweets() == 0


class TestMentionedTweets(TestCase):

    def testMultipleMentionsAndNoEmbeds(self):
        article = _load_fixture("guardian.html")
        assert article.mentions_tweets() is True
        assert article.embeds_tweets() is False
        mentions = article.list_mentioned_tweets()
        assert len(mentions) == article.count_mentioned_tweets()
        assert len(mentions) == 3

    def testNoMentions(self):
        article = _load_fixture("npr.html")
        assert article.mentions_tweets() is False
        assert article.count_mentioned_tweets() == 0


class TestParsing(TestCase):

    def testUrlLoading(self):
        url_article = Article(url="https://www.foxbusiness.com/lifestyle/gas-prices-increasing-midwest-memorial-day-weekend")
        html_article = _load_fixture('fox-business.html')
        assert url_article.get_html()[0:40] == html_article.get_html()[0:40]
        assert url_article.get_content()[0:40] == html_article.get_content()[0:40]

    def testBadIntialization(self):
        try:
            _ = Article()
            assert False
        except ValueError:
            assert True

    def testGetContent(self):
        article = _load_fixture("fox-business.html")
        content = article.get_content()
        assert content.startswith('<html><body><div><div class="article-body">')

    def testGetHtml(self):
        article = _load_fixture("fox-business.html")
        html = article.get_html()
        assert html.startswith('<!doctype html>')
