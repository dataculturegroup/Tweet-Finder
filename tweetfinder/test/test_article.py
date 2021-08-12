import os
from unittest import TestCase
from goose3 import Goose

from tweetfinder import Article

this_dir = os.path.dirname(os.path.abspath(__file__))
fixtures_dir = os.path.join(this_dir, "fixtures")


'''
This utilizes a few webpages as static test cases:
 * [guardian](https://www.theguardian.com/world/2021/may/13/how-covid-lockdown-forged-unlikely-friendships)
 * [npr](https://www.npr.org/sections/health-shots/2021/05/18/997461471/its-time-for-americas-fixation-with-herd-immunity-to-end-scientists-say) 
 * [cnn](https://www.cnn.com/us/live-news/san-jose-ca-shooting-05-26-21/h_41658163e6c6f2416d346adb6c01119f)
 * [time](https://time.com/4263227/most-popular-tweets/)
'''


def _load_fixture(filename, return_article=True):
    # If the article has a link to a twitter account that should not return as an embed
    with open(os.path.join(fixtures_dir, filename)) as f:
        article_html = f.read()
    if return_article:
        article = Article(html=article_html)
        return article
    return article_html


class TestEmbeddedTweets(TestCase):

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

    def testMultipleMentionsAndNoEmbeds(self):
        article = _load_fixture("guardian.html")
        assert article.mentions_tweets() is True
        assert article.embeds_tweets() is False
        mentions = article.list_mentioned_tweets()
        assert len(mentions) == article.count_mentioned_tweets()
        assert len(mentions) == 2

    def testMentionInLinkNotText(self):
        # this article has a mention in a link - "tweets" - not in text so that shouldn't count
        article = Article("https://www.theguardian.com/film/2020/jan/01/the-most-exciting-movies-of-2020-horror")
        assert article.mentions_tweets() is False

    def testNoMentions(self):
        article = _load_fixture("npr.html")
        assert article.mentions_tweets() is False
        assert article.count_mentioned_tweets() == 0


class TestParsing(TestCase):

    def testBadIntialization(self):
        try:
            _ = Article()
            assert False
        except ValueError:
            assert True

    def testGetContent(self):
        article = _load_fixture("npr.html")
        content = article.get_content()
        assert content.startswith('<html><body><div><div id="storytext" class="storytext storylocation linkLocation">')

    def testGetHtml(self):
        article = _load_fixture("npr.html")
        html = article.get_html()
        assert html.startswith('<!doctype html>')
