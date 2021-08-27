import json
import os

import pandas as pd
import logging
import time
from goose3 import Goose

from tweetfinder import Article

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

FROM_CSV = False

# must have a `stories_id` and `url` column in it (we source random_stories for testing from Media Cloud)
STORY_CSV_FILE = "scripts/2021-random-random_stories.csv"

stories_df = pd.read_csv(STORY_CSV_FILE)
logger.info("Loaded {} random_stories from {}".format(len(stories_df.index), STORY_CSV_FILE))

directory = 'scripts/stories/random_stories'
article_jsons = []
for json_file in os.listdir(directory):
    if 'json' in json_file:
        with open(directory + '/' + json_file) as f:
            article_json = json.load(f)
            article_jsons.append(article_json)

def count_tweets_goose(html):
    g = Goose()
    article = g.extract(raw_html=html)
    tweet_embed_count = len(article.tweets)
    return tweet_embed_count

# observed_tweets:
goose_tweets_list = []
goose_tweets_js_list = []
tweetfinder_tweets_list = []
tweetfinder_tweets_js_list = []
url_list = []
stories_id_list = []
ref_tweet_count = []
has_embed_list = []
has_ref_list = []
for article_json in article_jsons:
    try:
        url = article_json['url']
        article = Article(url=url)
        article_js = Article(url=url, timeout=30)
        url_list.append(url)
        stories_id_list.append(article_json['stories_id'])
        tweetfinder_tweets_list.append(article.count_embedded_tweets())
        tweetfinder_tweets_js_list.append(article_js.count_embedded_tweets())
        goose_tweets_list.append(count_tweets_goose(article.get_html()))
        goose_tweets_js_list.append(count_tweets_goose(article_js.get_html()))
        ref_tweet_count.append(article.count_mentioned_tweets())
        has_embed_list.append(article.embeds_tweets())
        has_ref_list.append(article.mentions_tweets())
    except:
        # probably a fetch or parse error, so just ignore the story
        continue

story_tester_df = pd.DataFrame({
    'url': url_list,
    'stories_id': stories_id_list,
    'goose_tweets': goose_tweets_list,
    'goose_tweets_js': goose_tweets_js_list,
    'tweet_finder_tweets': tweetfinder_tweets_list,
    'tweet_finder_js_tweets': tweetfinder_tweets_js_list,
    'ref_tweet_count': ref_tweet_count,
    'has_embeds': has_embed_list,
    'has_refs': has_ref_list
})
story_tester_df.to_csv('evaluation-results-{}.csv'.format(time.strftime("%Y%m%d-%H%M%S")), index=False)
