import unittest

from tweetfinder import Article


class TweetFinderTests(unittest.TestCase):

    def setUp(self):
        self.embedded_article = Article(
            url='https://www.foxbusiness.com/lifestyle/gas-prices-increasing-midwest-memorial-day-weekend')
        self.reference_only_article = Article(
            url='https://www.theguardian.com/world/2021/may/13/how-covid-lockdown-forged-unlikely-friendships')
        self.empty_article = Article(
            url='https://www.npr.org/sections/health-shots/2021/05/18/997461471/its-time-for-americas-fixation-with-herd-immunity-to-end-scientists-say')

    def test_nothing_passsed_in(self):
        try:
            nothing_article = Article()
            assert False
        except ValueError:
            assert True

    # count referenced tweets
    def test_count_referenced_tweets_ref_only(self):
        reference_only_tweet_refs = self.reference_only_article.count_mentioned_tweets()
        assert reference_only_tweet_refs == 3

    def test_count_referenced_tweets_embeds_only(self):
        embeds_tweet_refs = self.embedded_article.count_mentioned_tweets()
        assert embeds_tweet_refs == 6

    def test_count_referenced_tweets_empty_article(self):
        empty_article_tweet_refs = self.empty_article.count_mentioned_tweets()
        assert empty_article_tweet_refs == 0

    # count embedded tweets
    def test_count_embedded_tweets_ref_only(self):
        embeds = self.reference_only_article.count_embedded_tweets()
        assert embeds == 0

    def test_count_embedded_tweets_embeds_only(self):
        embeds = self.embedded_article.count_embedded_tweets()
        assert embeds == 4

    def test_count_embeds_tweets_empty_article(self):
        embeds = self.empty_article.count_embedded_tweets()
        assert embeds == 0

    # list referenced tweets
    def test_list_referenced_tweets_ref_only(self):
        reference_only_tweet_refs = self.reference_only_article.list_mentioned_tweets()
        reference_1 = {'start_index': 0, 'phrase': ''}
        reference_2 = {'start_index': 0, 'phrase': ''}
        reference_3 = {'start_index': 0, 'phrase': ''}
        refs_list = [reference_1, reference_2, reference_3]
        assert reference_only_tweet_refs == refs_list

    def test_list_referenced_tweets_embeds_only(self):
        embeds_tweet_refs = self.embedded_article.list_mentioned_tweets()
        reference_1 = {'start_index': 0, 'phrase': ''}
        reference_2 = {'start_index': 0, 'phrase': ''}
        reference_3 = {'start_index': 0, 'phrase': ''}
        reference_4 = {'start_index': 0, 'phrase': ''}
        reference_5 = {'start_index': 0, 'phrase': ''}
        reference_6 = {'start_index': 0, 'phrase': ''}
        refs_list = [reference_1, reference_2, reference_3, reference_4, reference_5, reference_6]
        assert embeds_tweet_refs == refs_list

    def test_list_referenced_tweets_empty_article(self):
        empty_article_tweet_refs = self.empty_article.list_mentioned_tweets()
        assert len(empty_article_tweet_refs) == 0

    # list embedded tweets
    def test_list_embedded_tweets_ref_only(self):
        embeds = self.reference_only_article.list_embedded_tweets()
        assert len(embeds) == 0

    def test_list_embedded_tweets_embeds_only(self):
        embeds = self.embedded_article.list_embedded_tweets()
        tweet_1 = {'tweet_id': 0, 'username': '', 'full_url': ''}
        tweet_2 = {'tweet_id': 0, 'username': '', 'full_url': ''}
        tweet_3 = {'tweet_id': 0, 'username': '', 'full_url': ''}
        tweet_4 = {'tweet_id': 0, 'username': '', 'full_url': ''}
        embed_list = [tweet_1, tweet_2, tweet_3, tweet_4]
        assert embeds == embed_list

    def test_list_embeds_tweets_empty_article(self):
        embeds = self.empty_article.list_embedded_tweets()
        assert len(embeds) == 0

    # get content
    def test_get_content(self):
        content = self.embedded_article.get_content()
        assert content == ''

    # get html
    def test_get_html(self):
        html = self.embedded_article.get_html()
        assert html == ''

    # references tweets
    def test_references_tweets(self):
        references_embedded_article = self.embedded_article.mentions_tweets()
        references_refs_only_article = self.reference_only_article.mentions_tweets()
        references_empty_article = self.empty_article.mentions_tweets()
        assert references_empty_article is False and references_embedded_article is True and \
               references_refs_only_article is True

    # embeds tweets
    def test_embeds_tweets(self):
        embeds_embedded_article = self.embedded_article.embeds_tweets()
        embeds_refs_only_article = self.reference_only_article.embeds_tweets()
        embeds_empty_article = self.empty_article.embeds_tweets()
        assert embeds_empty_article is False and embeds_refs_only_article is False and \
               embeds_embedded_article is True
