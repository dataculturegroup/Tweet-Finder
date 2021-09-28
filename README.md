Tweet Finder
============

**A small Python library for finding Tweets embedded in online news articles, and mentions of Tweets**. We wrote this
because we suspected that current research approaches were significantly under-counting the number of Tweets embedded 
in online news stories. Our initial evaluation confirms this.

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
