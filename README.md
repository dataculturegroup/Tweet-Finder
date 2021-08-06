Tweet Finder
============

A simple Python library for finding Tweets embedded, and mentions of Tweets, in online news articles.

Quickstart
----------

Install with pip: `pip install tweetfinder`.

```python
from tweetfinder import Article
my_article = Article(url="http://my.news/article")  # this will load and parse the article
my_article.count_references()
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
