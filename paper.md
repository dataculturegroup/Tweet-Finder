---
title: 'tweetfinder: Finding Embedded Tweets and Mentions of Tweets in Online News with Python'
tags:
  - Python
  - news
  - Twitter
authors:
  - name: Rahul Bhargava^[corresponding author]
    orcid: 0000-0003-3904-4302
    affiliation: 1
  - name: Dina Zemlyanker
    affiliation: 1
affiliations:
 - name: Northeastern University
   index: 1
date: 10 November 2021
bibliography: paper.bib
---

# Summary

The use of embedded content from Twitter, YouTube, TikTok, and other platforms has grown to become a norm in online news content. When these platforms emerged journalists employed existing industry norms to treat them like traditional sources [@hermida_tweets_2012] [@vis_twitter_2013]. Twitter in particular has become a major platform used by journalists and politicians alike. This has led to a pivot in research work to instead address Twitter as a platform of authority, where news needing coverage is being made [@molyneux_when_2021]. Research to understand the evolution and current practice of using tweets in online news relies on large scale automated analysis to discover embedded tweets, and mentions of tweets, in articles. Finding embedded tweets, and mentions of tweets, can be considered a specialized content extraction task [@gruppi_tweeting_2021].

# Statement of Need

`tweetfinder` is a Python library that extract embedded tweets and mentions of twitter from online news content. Performing the technical task of locating embedded content accurately is critical for making accurate research conclusions about Twitter’s role in online news (an active research area). As journalist digital practices evolve, the technical approaches to embedding tweets have diverged from just following Twitter’s guidelines. After reviewing existing state of the art, we found significant amounts of content was missed.

# Functionality

Users can provide `tweetfinder` with a URL or raw HTML text as input, and it provides convenience methods to return lists of those two types of references to Tweets it finds. HTML is fetched via `requests`[@requests], content is extracted via `readability-lxml`[@python-readability], and further manipulated via `BeautifulSoup` [@beautifulsoup].

## Finding Embedded Tweets

Twitter’s documentation offers a “supported” approach to embedding tweets in web content - namely inserting it via a `<blockquote class=”twitter-tweet”>` tag [@twitter_help]. We found that not all websites follow these guidelines, and hypothesized that prior work relying on this method of counting could be undercounting. In addition, evolving norms of web-app development have led to some news sites taking an approach of rendering their HTML content via client-side Javascript, leading to non-standard embedding.

`tweetfinder` includes a list of possible formats for embedding:
 * `blockquote` elements classed of “twitter-tweet” (the officially supported approach)
 * `blockquote` elements with a child `a` node linking to twitter.com
 * `div` elements classed “embed-twitter”
 * `div` elements classed “twitter-tweet-rendered” with a child `iframe`

We also provide examples of how to pre-process a URL through a browser so any Javascript is able to run fully (via `selenium` [@selenium]). While computationally expensive, this approach does ensure more complete results.

## Finding Mentions of Twitter

A second key functionality for researchers is to find mentions of tweets in news. Existing work takes the approach of building libraries of phrases and keywords and checking content against them [@rony_large-scale_2018, @molyneux_when_2021]. `tweetfinder` integrates prior keyword lists and expands them to allow users to locate these types of mentions of twitter content in news online. A clear limitation is that this approach currently only works for English language content; `tweetfinder` uses `cld2`[@pycld2] to detect the content language and raises an error if the user attempts to list mentions on non-English language articles.

# Results

To characterize and evaluate performance we assessed against three different corpora:
 * 2021 manual: 41 hand-picked articles, manually reviewed to identify the ids of all embedded tweets
 * 2021 random: A set of 500 random articles from 2021
 * 2020 relevant: A set of 1000 random articles from 2020, all including “tweet”, “tweeted”, or “twitter”

Each of those corpora were created from the Media Cloud database of news stories from national US media sources [@roberts_media_2021].

## Embedded Tweets

In our literature review we found the most commenly used library for extracting embedded tweets was `Goose` [@goose3]; it was either cited directly in each paper referenced here, or we contacted the authors and they indicated that they used it. In order to evaluate performance we compared the tweets found by `tweetfinder` to `Goose` in our manually coded corpus. This allows us to look at precision and recall for each library.

| Library | Tweets Found | Precision | Recall |
| --- | --- | --- | --- |
| manual reivew | 40 | 1 | 1 |
| tweetfinder | 26 | 0.925 | 0.694 |
| tweetfinder (with Javascript) | 37 | 0.946 | 0.972 |
| Goose | 22 | 0.956 | 0.611 |

Unsurprisingly, precision is high for all three automated approaches (Table 1). Recall varies far more. This small corpus shows processing the Javascript is critical for finding a higher percentage of the total embedded tweets. In this analysis we omit a “Goose (with Javascript)” option because executing the Javascript replaces the `blockquote` element with an `iframe` element, leaving Goose unable to detect embedded tweets at all.

| Library | 2021 manual | 2021 random | 2020 relevant |
| --- | --- | --- | --- |
| tweetfinder | 26 | 24 | 601 |
| tweetfinder (with Javascript) | 37 | 28 | 844 |
| Goose | 22 | 22 | 469 |

At a higher level, in each of these corpora we see `tweetfinder` outperforming `Goose` (Table 2). It is particularly worth highlighting the 2020 relevant results, which were selected to more likely include such content. On this corpus of stories, `tweetfinder` finds more finds 28% more embedded tweets than `Goose`, and `tweetfinder` (with Javascript) finds 80% more.

## Mentions of Tweets

This feature does not lend itself to evaluation in the same manner as finding embedded tweets, because the software is simply finding predetermined strings in text. Instead, we characterize the quantity of mentions found in each corpus against each set of included phrases. We include three separate lists of phrases:
 * Basic: A short list of basic phrases associated with Twitter generated by the authors of this paper (examples: “tweeted”, “in a tweet”)
 * Rony 2018: A list shared by the authors in their paper [@rony_large-scale_2018] (examples: “posted on Twitter”, “tweet sent”, “wrong on twitter”)
 * Molyneux 2020: A short list shared by authors in their paper [@molyneux_when_2021] (examples: “retweet”, “according to a tweet”)


 | Corpus | Total mentions | Basic | Rony 2018 | Molyneux 2020 |
 | --- | --- | --- | --- | --- |
 | 2021 Manual | 61 | 53 | 60 | 1 |
 | 2021 Random | 37 | 35 | 37 | 1 |
 | 2020 Relevant | 936 | 768 | 935 | 44 |

Table 3 shows that the very short “Basic” list finds a significant portion of the mentions that are included in the far longer Rony 2018 list. This suggests that the majority of journalists use only a small set of phrases when mentioning twitter content in articles.

# Conclusion

These types of libraries are critical to help accurately describe how users and events on Twitter are spilling over into more mainstream news coverage. If deployed at scale, this capability to find content more robustly could help identify types of Twitter-related news stories and track their prevalence over time.

#References
