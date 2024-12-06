#! /usr/bin/env python
from setuptools import setup
import re
from os import path

with open('tweetfinder/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='tweetfinder',
      version=version,
      description='Find tweets embedded and mentioned in news articles online.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Rahul Bhargava',
      author_email='r.bhargava@northeastern.edu',
      packages=['tweetfinder', 'tweetfinder.test'],
      data_files=[
          ('data', ['tweetfinder/data/twitter-patterns-rony-2018.txt']),
      ],
      include_package_data=True,
      install_requires=[
          "requests",
          "readability-lxml==0.8.1",
          "py3langid==0.3.*",
          "beautifulsoup4==4.12.*",
          "lxml_html_clean==0.4.*",
      ],
      project_urls={
          "Source": "https://github.com/dataculturegroup/Tweet-Finder",
          "Docs": "https://tweet-finder.readthedocs.io/",
      },
      license='Apache',
      zip_safe=False
)
