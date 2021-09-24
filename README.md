Tweet Finder
============

A small Python library for finding Tweets embedded in online news articles, and mentions of Tweets.

Quickstart
----------

Install with pip: `pip install tweetfinder`.

```python
from tweetfinder import Article
my_article = Article(url="http://my.news/article")  # this will load and parse the article

# you can list discover all the tweets that are embedded in the HTML 
num_embedded = my_article.count_embedded_tweets()
tweets_embedded = my_article.list_embedded_tweets() # metadata about tweets that are embedded

# you can also discover any mentions of twitter (in English), like "tweeted that" or "in a retweet"
num_mentions = my_article.count_mentioned_tweets()
tweet_mentions = my_article.list_mentioned_tweets()  # list of text snippets that mention a tweet 
```


API
---

TODO


Development
-----------

If you want to work on this module, clone the repo and install dependencies: `make requirements-dev`.

## Distribution

1. Run `make test` to make sure all the test pass
2. Update the version number in `tweetfinder/__init__.py`
3. Make a brief note in the version history section below about the changes
4. Run `make build-release` to create an install package
5. Run `make release-test` to upload it to PyPI's test platform
6. Run `make release` to upload it to PyPI


Version History
---------------

* __v0.1.0__: initial release for testing


Authors
-------

 * Rahul Bhargava
 * Dina Zemlyanker
