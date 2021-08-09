import pandas as pd
import logging
import time

from tweetfinder import Article

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

# must have a `stories_id` and `url` column in it (we source stories for testing from Media Cloud)
STORY_CSV_FILE = "2021-random-stories.csv"

stories_df = pd.read_csv(STORY_CSV_FILE)
logger.info("Loaded {} stories from {}".format(len(stories_df.index), STORY_CSV_FILE))

url_list = []
stories_id_list = []
tweet_id_list = []
embedded_tweet_count_list = []
ref_tweet_count = []
has_embed_list = []
has_ref_list = []
for index, row in stories_df.iterrows():
    url = row['url']
    article = Article(url=row['url'])
    url_list.append(url)
    stories_id_list.append(row['stories_id'])
    embedded_tweet_count_list.append(article.count_embedded_tweets())
    ref_tweet_count.append(article.count_mentioned_tweets())
    has_embed_list.append(article.embeds_tweets())
    has_ref_list.append(article.mentions_tweets())

story_tester_df = pd.DataFrame({
    'url': url_list,
    'stories_id': stories_id_list,
    'embedded_tweet_count': embedded_tweet_count_list,
    'ref_tweet_count': ref_tweet_count,
    'has_embeds': has_embed_list,
    'has_refs': has_ref_list
})
story_tester_df.to_csv('evaluation-results-{}.csv'.format(time.strftime("%Y%m%d-%H%M%S")), index=False)
