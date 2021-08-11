from bs4 import BeautifulSoup
import readability
import requests
import pycld2 as cld2

from . import mentions


class UnsupportedLanguageException(BaseException):

    def __init__(self, language:str):
        self.language = language
        super().__init__("Finding mentions is only supported in English right now (not {})".format(self.language))


class Article:

    def __init__(self, url: str = None, html: str = None, mentions_list: list = None):
        if (url is None) and (html is None):
            raise ValueError('You must pass in either a url or html argument')
        self._mentions_list = mentions_list or mentions.ALL
        self._url = url
        if html is None:
            self._html = self._download_article()
        else:
            self._html = html
        self._process()

    def _download_article(self):
        url = self._url
        r = requests.get(url)
        return r.text.lower()

    def _process(self):
        self._document = readability.Document(self._html)
        self._content = self._document.summary()
        self._soup = BeautifulSoup(self._html, "lxml")
        self._embeds = self._find_embeds()
        self._mentions = self._find_mentions()

    def get_html(self):
        return self._html

    def get_content(self):
        return self._content

    def embeds_tweets(self):
        return len(self._embeds) > 0

    def mentions_tweets(self):
        return len(self._mentions) > 0

    def count_embedded_tweets(self):
        """Get the count of embedded tweets in the article."""
        return len(self._embeds)

    def count_mentioned_tweets(self):
        """Get the count of tweet mentions in the article."""
        return len(self._mentions)

    def list_embedded_tweets(self):
        """Get a list of tweets from the article."""
        return self._embeds

    def list_mentioned_tweets(self):
        """Get a list of starting positions for each of the twitter mentions in the text."""
        return self._mentions

    def _find_embeds(self):
        tweets = []
        # Twitter recommends embedding as block quotes
        blockquotes = self._soup.find_all('blockquote')
        for b in blockquotes:
            is_embedded_tweet = False
            # check the official way of doing it
            if b['class'] == 'twitter-tweet':
                is_embedded_tweet = True
            # But we found some sites don't use that class, so check if there is a link to twitter in there.
            # In our experimentation this produces better results than just checking the class.
            links = b.find_all('a')
            twitter_link = None
            for link in links:
                if 'twitter.com' in link['href']:
                    is_embedded_tweet = True
                    twitter_url = link['href']
            if is_embedded_tweet:
                username_start_index = twitter_url.find('@')
                username = twitter_url[username_start_index:-1]
                tweet_id_start_index = twitter_url.find('/')
                tweet_id = twitter_url[tweet_id_start_index:-1]
                tweet_info = {'tweet_id': tweet_id, 'username': username, 'full_url': twitter_url}
                tweets.append(tweet_info)
        # some people (CNN, others) embed with JS
        divs = self._soup.find_all('div', class_="embed-twitter")
        for d in divs:
            if d['data-embed-id']:
                tweet_info = {'tweet_id': d['data-embed-id']}
                tweets.append(tweet_info)
        return tweets

    def _validate_language(self) -> bool:
        valid_languages = ['en']
        is_reliable, _, details = cld2.detect(self._content)
        detected_language = details[0][1]
        if is_reliable and ( detected_language not in valid_languages):
            raise UnsupportedLanguageException(detected_language)

    def _find_mentions(self):
        self._validate_language()
        # find the first occurrence of the twitter phrase, then continue searching for the
        # next occurrence of the twitter phrase from the index of end of the current twitter phrase
        # instance until there are no more twitter phrases located
        mentions_dict_list = []
        article_text = self._content
        for twitter_phrase in self._mentions_list:
            start_index = 0
            phrase_index = 0
            while phrase_index != -1:
                phrase_index = article_text.find(twitter_phrase, start_index)
                start_index = phrase_index + len(twitter_phrase)
                if phrase_index != -1:
                    mention_dict = {'start_index': start_index, 'phrase': twitter_phrase}
                    mentions_dict_list.append(mention_dict)
        # returns a tuple of the twitter phrase count and a list of the starting indices of each of the
        # twitter phrases
        return mentions_dict_list
