from html.parser import HTMLParser
import readability
from goose3 import Goose
import requests
import pycld2 as cld2

from . import mentions


class UnsupportedLanguageException(object):

    def __init__(self, language:str):
        self.language = language
        super().__init__("Finding mentions is only supported in English right now (not {})".format(self.language))


class Article:

    def __init__(self, url: str = None, html: str = None, mentions_list: list = mentions.ALL):
        if (url is None) and (html is None):
            raise ValueError('You must pass in either a url or html argument')
        self.mentions_list = mentions_list
        self.url = url
        if html is None:
            self.html = self._download_article()
        else:
            self.html = html
        self.content = self._process()

    def _download_article(self):
        url = self.url
        r = requests.get(url)
        return r.text.lower()

    def _process(self):
        html = self.html
        article_text = readability.Document(html)
        return article_text

    def get_html(self):
        return self.html

    def get_content(self):
        return self.content

    def embeds_tweets(self):
        embeds = self.count_embedded_tweets()
        return embeds > 0

    def mentions_tweets(self):
        mentions = self.count_mentioned_tweets()
        return mentions > 0

    def count_embedded_tweets(self):
        """Get the count of embedded tweets in the article."""
        goose = self._get_tweets_goose()
        goose_count = goose[0]
        calc = self._get_calc_tweets()
        calc_count = calc[0]
        if goose_count >= calc_count:
            return goose_count
        return calc_count

    def count_mentioned_tweets(self):
        """Get the count of tweet mentions in the article."""
        twitter_mentions = self._get_twitter_phrases()
        return twitter_mentions[0]

    def list_embedded_tweets(self):
        """Get a list of tweets from the article."""
        goose_tweets = self._get_tweets_goose()
        calc_tweets = self._get_calc_tweets()
        calc_tweet_list = calc_tweets[1]
        goose_tweet_list = goose_tweets[1]
        if len(goose_tweet_list) > len(calc_tweet_list):
            return goose_tweet_list
        return calc_tweet_list

    def list_mentioned_tweets(self):
        """Get a list of starting positions for each of the twitter mentions in the text."""
        twitter_mentions = self._get_twitter_phrases()
        return twitter_mentions[1]

    def _get_calc_tweets(self):
        article_text = self.content
        html_parser = MyHTMLParser()
        html_parser.feed(article_text.summary())
        tweet_embed_count = html_parser.tweet_embed_count
        tweet_list = html_parser.tweet_list
        return tweet_embed_count, tweet_list

    def _get_tweets_goose(self):
        g = Goose()
        article = g.extract(raw_html=self.html)
        tweet_count = len(article.tweets)
        return tweet_count, article.tweets

    def _validate_language(self) -> bool:
        valid_languages = ['en']
        isReliable, textBytesFound, details = cld2.detect(self.content)
        detected_language = details[0][1]
        if isReliable and ( detected_language not in valid_languages):
            raise UnsupportedLanguageException(detected_language)

    def _get_twitter_phrases(self):
        self._validate_language()
        twitter_phrase_count = 0
        # find the first occurrence of the twitter phrase, then continue searching for the
        # next occurrence of the twitter phrase from the index of end of the current twitter phrase
        # instance until there are no more twitter phrases located
        mentions_dict_list = []
        article_text = self.content.summary()
        for twitter_phrase in self.mentions_list:
            start_index = 0
            phrase_index = 0
            while phrase_index != -1:
                phrase_index = article_text.find(twitter_phrase, start_index)
                start_index = phrase_index + len(twitter_phrase)
                if phrase_index != -1:
                    twitter_phrase_count += 1
                    mention_dict = {'start_index': start_index, 'phrase': twitter_phrase}
                    mentions_dict_list.append(mention_dict)
        # returns a tuple of the twitter phrase count and a list of the starting indices of each of the
        # twitter phrases
        return twitter_phrase_count, mentions_dict_list


class MyHTMLParser(HTMLParser):

    def __init__(self):
        self.tweet_embed_count = 0
        self.twitter_phrase_count = 0
        self.tweet_list = []
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        # check for anchor tags
        if tag == 'a':
            # check if href is defined in the anchor tag
            for name, value in attrs:
                if name == 'href':
                    # check if twitter.com is in the href url
                    if 'twitter.com' in value:
                        self.tweet_embed_count += 1
                        username_start_index = value.find('@')
                        username = value[username_start_index:-1]
                        tweet_id_start_index = value.find('/')
                        tweet_id = value[tweet_id_start_index:-1]
                        tweet_dict = {'tweet_id': tweet_id , 'username': username , 'full_url': value}
                        self.tweet_list.append(tweet_dict)
