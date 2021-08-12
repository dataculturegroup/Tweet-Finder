import pandas as pd
import logging
import time
import os
import json

from tweetfinder import Article, UnsupportedLanguageException

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

FROM_CSV = False

# each file in a json with a `raw_first_download_file` attribute that has the HTML of the webpage
# these are pulled from Media Cloud, but not committed to the directory due to copyright concerns
STORY_FILE_DIR = os.path.join("scripts", "stories")

logger.info("Loading story files from {}".format(STORY_FILE_DIR))

url_list = []
stories_id_list = []
tweet_id_list = []
embedded_tweet_count_list = []
ref_tweet_count = []
has_embed_list = []
has_ref_list = []

for file in os.listdir(STORY_FILE_DIR):
    f = os.path.join(STORY_FILE_DIR, file)
    try:
        with open(f) as filename:
            story = json.load(filename)
        article = Article(html=story['raw_first_download_file'])
        url_list.append(story['url'])
        stories_id_list.append(story['stories_id'])
        embedded_tweet_count_list.append(article.count_embedded_tweets())
        ref_tweet_count.append(article.count_mentioned_tweets())
        has_embed_list.append(article.embeds_tweets())
        has_ref_list.append(article.mentions_tweets())
    except json.decoder.JSONDecodeError:
        # just skip the story if it doesn't open right
        continue
    except UnsupportedLanguageException:
        # can't detect language, so just skip
        continue


story_tester_df = pd.DataFrame({
    'url': url_list,
    'stories_id': stories_id_list,
    'embedded_tweet_count': embedded_tweet_count_list,
    'ref_tweet_count': ref_tweet_count,
    'has_embeds': has_embed_list,
    'has_refs': has_ref_list
})
story_tester_df.to_csv('evaluation-results-{}.csv'.format(time.strftime("%Y%m%d-%H%M%S")), index=False)
