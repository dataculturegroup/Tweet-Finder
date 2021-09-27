"""
The main module to support finding embedded tweets and mentions of tweets in online news.
"""

from bs4 import BeautifulSoup
import readability
import re
import requests
import logging
import pycld2 as cld2
from typing import List, Dict

from . import mentions

logger = logging.getLogger(__name__)

# when we find a mention, we include this many characters of context before and after it
MENTIONS_CONTEXT_WINDOW_SIZE = 100

# how many seconds to wait when trying to load a webpage via GET
DEFAULT_TIMEOUT = 5

# modified from https://stackoverflow.com/questions/4138483/twitter-status-url-regex
tweet_status_url_pattern = re.compile('^https?:\/\/twitter\.com\/(?:#!\/)?(\w+)\/status(es)?\/(\d+).*', re.IGNORECASE)


class UnsupportedLanguageException(BaseException):
    """Helper class thrown when tying to parse mentions in a language that isn't supported."""

    def __init__(self, language: str):
        self.language = language
        super().__init__("Finding mentions is only supported in English right now (not {})".format(self.language))


class Article:
    """
    This is how you parse an article for embeds and mentions of Tweets. Pass in a `url` or `html` to the constructor.
    Then call any of the `get_` methods to see what the code found.
    """

    def __init__(self, url: str = None, html: str = None, mentions_list: list = None, timeout: int = None):
        """
        Process an online news article to find embedded tweets and mentions of tweets. Send in either `url` or
        `html`.
        :param url: Option A: Pass in a URL to an available news story online. This will be fetched for you and content
        will be extract via the readability library.
        :param html: Option B: Pass in html text to be parsed.
        :param mentions_list: Pass in a custom list of snippets that count as "mentions" or tweets. The default is to
        use the ones in `mentions.ALL`. You can use another subset from that module, or provide your own.
        :param timeout: If you pass in `url`, you can customize how long to wait before timing out the request if the
        server doesn't respond. The default value is `DEFAULT_TIMEOUT` (5 seconds).
        """
        if (url is None) and (html is None):
            raise ValueError('You must pass in either a url or html argument')
        self._url = url
        self._mentions_list = mentions_list or mentions.ALL
        self._download_timeout = timeout or DEFAULT_TIMEOUT
        if html is None:
            self._html = self._download_article()
        else:
            self._html = html
        self._process()

    def _download_article(self) -> str:
        """
        Internal help to download html from a URL and return the full content.
        :return:
        """
        url = self._url
        r = requests.get(url, timeout=self._download_timeout)
        return r.text.lower()

    def _process(self) -> None:
        """
        Parse the HTML and find embedded tweets, and mentions.
        :return:
        """
        self._html_soup = BeautifulSoup(self._html, "lxml")
        # remove HTML tags so we can search text-only content for mentions later
        doc = readability.Document(self._html)
        self._content = doc.summary()
        self._content_soup = BeautifulSoup(self._content, "lxml")
        self._content_no_tags = self._content_soup.get_text().strip()
        # lets parse it all here so we don't have to do it more than once
        self._embeds = self._find_embeds()
        self._mentions = self._find_mentions()

    def get_html(self) -> str:
        """Return the HTML fetched if you passed in a url, or the same HTML you passed in if not."""
        return self._html

    def get_content(self) -> str:
        """Return the part of the webpage that we considered as content, via the readability library."""
        return self._content

    def embeds_tweets(self) -> bool:
        """Does this webpage have any embedded tweets?"""
        return len(self._embeds) > 0

    def mentions_tweets(self) -> int:
        """Does this webpage mention any tweets?"""
        return len(self._mentions) > 0

    def count_embedded_tweets(self):
        """How many tweets are embedded on this webpage?"""
        return len(self._embeds)

    def count_mentioned_tweets(self):
        """How many times are tweets mentioned on this webpage?"""
        return len(self._mentions)

    def list_embedded_tweets(self) -> List[Dict]:
        """
        Detailed information about the tweets embedded on the webpage.
        :return: The exact info depends on how the tweets were embeded. If they were embedded the official way, then
        we can return a link to the tweet, the tweet id, and the author's username. But there are some other ways
        tweets are embededed via Javascript that only let us parse out the tweet id easily. So you can check the
        `html_source` property of each returned one to identify how we found it and then look for other data based on
        that. You will at least get the tweet id no matter which method we found it with.
        """
        return self._embeds

    def list_mentioned_tweets(self) -> List[Dict]:
        """
        Detailed information about each mention of a tweet we found=.
        :return: None if this isn't a supported language, otherwise a List. Each item includes the `phrase` found,
        some `context` via a window of text around it, and `content_start_index` to help you find it yourself in
        the `get_content` string.
        """
        return self._mentions

    def _find_embeds(self) -> List[Dict]:
        """Search content for any embedded tweets via a variety of methods."""
        tweets = []
        # Twitter recommends embedding as block quotes
        blockquotes = self._html_soup.find_all('blockquote')
        for b in blockquotes:
            is_embedded_tweet = False
            # check the official way of doing it
            if b.has_attr('class') and ('twitter-tweet' in b['class']):  # this is an array of the CSS classes
                is_embedded_tweet = True
            # But we found some sites don't use that class, so check if there is a link to twitter in there.
            # In our experimentation this produces better results than just checking the class.
            links = b.find_all('a')
            twitter_url = None
            for link in links:
                if link.has_attr('href') and ('twitter.com' in link['href']):
                    is_embedded_tweet = True
                    twitter_url = link['href']
            if is_embedded_tweet:
                try:
                    info = tweet_status_url_pattern.match(twitter_url).groups()
                    tweet_info = dict(tweet_id=info[2], username=info[0], full_url=twitter_url,
                                      html_source='blockquote url pattern')
                except Exception:  # some other format
                    username_start_index = twitter_url.find('@')
                    username = twitter_url[username_start_index:-1]
                    tweet_id_start_index = twitter_url.find('/')
                    tweet_id = twitter_url[tweet_id_start_index:-1]
                    tweet_info = dict(tweet_id=tweet_id, username=username, full_url=twitter_url,
                                      html_source='blockquote url fallback')
                tweets.append(tweet_info)
        # some people do it differently, (CNN, others) embed with like this
        divs = self._html_soup.find_all('div', class_="embed-twitter")
        for d in divs:
            if d.has_attr('data-embed-id'):
                tweet_info = dict(tweet_id=d['data-embed-id'], html_source='div with data-embed-id')
                tweets.append(tweet_info)
        # check if we are looking at HTML already rendered by JS and transformed into an iframe of content
        divs = self._html_soup.find_all('div', class_="twitter-tweet-rendered")
        for d in divs:
            iframes = d.find_all('iframe')
            for iframe in iframes:
                if iframe.has_attr('data-tweet-id'):
                    tweet_info = dict(tweet_id=iframe['data-tweet-id'], html_source='rendered iframe')
                    tweets.append(tweet_info)
        return tweets

    def _validate_language(self):
        """Throw an error if this isn't a supported language for finding mentions."""
        valid_languages = ['en']
        try:
            is_reliable, _, details = cld2.detect(self._content)
            detected_language = details[0][1]
            if is_reliable and (detected_language not in valid_languages):
                raise UnsupportedLanguageException(detected_language)
        except cld2.error:
            # if there was some weird unicode then assume it isn't english
            raise UnsupportedLanguageException("Undetectable")

    def _find_mentions(self) -> List[Dict]:
        """
        Find the first occurrence of the twitter phrase, then continue searching for the next occurrence of the twitter
        phrase from the index of end of the current twitter phrase instance until there are no more twitter phrases
        located.
        :return: None if the language isn't supported, otherwise a list.
        """
        try:
            self._validate_language()  # bail if this isn't in english
        except UnsupportedLanguageException:
            return None
        mentions_dict_list = []
        article_text = self._content_no_tags
        for twitter_phrase in self._mentions_list:
            start_index = 0
            phrase_index = 0
            while phrase_index != -1:
                phrase_index = article_text.find(twitter_phrase, start_index)
                # this is the start index into the *content*, not the raw html
                start_index = phrase_index
                if phrase_index != -1:
                    context_start = max(0, phrase_index - MENTIONS_CONTEXT_WINDOW_SIZE)
                    context_end = min(len(article_text),
                                      phrase_index + len(twitter_phrase) + MENTIONS_CONTEXT_WINDOW_SIZE)
                    context = article_text[context_start:context_end]
                    mention_dict = {'phrase': twitter_phrase, 'context': context, 'content_start_index': start_index}
                    mentions_dict_list.append(mention_dict)
                    start_index = phrase_index + len(twitter_phrase)
        # returns a tuple of the twitter phrase count and a list of the starting indices of each of the
        # twitter phrases
        return mentions_dict_list
