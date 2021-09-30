tweetfinder: Find tweets embedded and mentioned in news articles online
=======================================================================

**Package on pypi**: https://pypi.org/project/tweetfinder/

**Code**: https://github.com/dataculturegroup/Tweet-Finder

**Documentation**: https://tweetfinder.readthedocs.io

**A small Python library for finding Tweets embedded in online news articles, and mentions of Tweets**. We wrote this
because we suspected that current research approaches were significantly under-counting the number of Tweets embedded 
in online news stories. Our initial evaluation confirms this.

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


Motivation
----------

Why are embedded tweets being undercounted? Two main reasons:

1. Not everyone embeds tweets following [the `blockquote` guidelines from Twitter](https://help.twitter.com/en/using-twitter/how-to-embed-a-tweet) 
2. Many new websites render their content via Javascript, not raw HTML so unless you run in a browser and execute the 
    Javascript, you won't see the embedded tweets on the page source 

Some of our initial numbers behind this:  

* Out of 1000 stories that mentioned twitter, our library found 640 embedded tweets in raw HTML
* [Goose3](https://goose3.readthedocs.io/en/latest/), which is what current papers seems to use, found 518 in the same
   set of stories (ie. it missed about 20%)
* If you add in support for processing Javascript-based embeds, we found 859 (35% more) that traditional raw HTML-based
   counting approaches miss 
   
These to-be-published results confirm our suspicion - most large quantitative news projects are under-counting 
embedded Tweets by around 35% or mre. This library is our attempt to help fix that.

Why does that matter? Understanding how Twitter (and other platforms) is used in news media is critical for building
a better map of how the media ecosystem functions. News shapes how we see the world; studying the architectures of 
information flows around us is critical for preventing the spread of hate speech, misinformation, and supporting
newsrooms and democracy. 


API
---

When you create an Article the HTML is downloaded (if needed) and parsed immediately to find any mentions
of twitter and any embedded tweets. There a number of methods to return the information found:

### my_article.embeds_tweets()

Return `True` or `False` depending on if there are any tweets embedded in the article.

### my_article.count_embedded_tweets()

Return the number of tweets embedded in the article.

### my_article.list_embedded_tweets()

Return a `list` of `dicts` with information about the tweets found. The properties in this `dict` depend on how
we found the tweet. It could look like this:

```python
[{
    'tweet_id': '//twitter.com/sliccard',
    'html_source': 'blockquote url fallback'
    'username': '',
    'full_url': 'https://twitter.com/sliccardo',
}]
```

Properties:
  * `tweet_id`: the unique id of the tweet, can be used in concert with Twitter's API to pull more metadata (always included) 
  * `html_source`: a string indicating which method the tweet was found with (always included)
  * `full_url`: the complete URL to the tweet on Twitter (sometimes included)
  * `username`: the twitter username of the author of the tweet, including the "@" (sometimes included)

### my_article.mentions_tweets()

Return `True` or `False` depending on if there are any mentions of tweets in the article.

### my_article.count_mentioned_tweets()

Return the number of mentions of tweets in the article.

### my_article.list_mentioned_tweets()


Development
-----------

If you want to work on this module, clone the repo and install dependencies: `make requirements-dev`.

## Distribution

1. Run `make test` to make sure all the test pass
2. Update the version number in `tweetfinder/__init__.py`
3. Make a brief note in the version history section below about the changes
4. Run `make sphinx-docs` to update the documentation
4. Run `make build-release` to create an install package
5. Run `make release-test` to upload it to PyPI's test platform
6. Run `make release` to upload it to PyPI


Version History
---------------

* __v0.1.0__: initial release for testing


Credits
-------

This library is part of the [Media Cloud](https://mediacloud.org) project, and is supported by the 
[Co-Lab for Data Impact](https://camd.northeastern.edu/research-scholarship-creative-practice/co-laboratory-for-data-impact/)
and the [Data Culture Group](https://dataculturegroup.org) at Northeastern University.

### Maintainers:
 * Rahul Bhargava
 * Dina Zemlyanker
