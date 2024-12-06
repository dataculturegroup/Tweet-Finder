"""
This script reads news URLs from a CSV and runs our code against them for evaluation. It compares parsing raw HTML,
HTML rendered by a headless browser so JS can run, and also runs Goose's extraction code. This produces a CSV we
can use for comparing how well our code performs in a few ways. This can take a long time to run:
* 35 mins for 500 stories (with a pool size of 8)
* 1.2 hours for 1000 stories with a pool size of 16)
"""

import pandas as pd
import logging
import time
from goose3 import Goose
from selenium import webdriver
import threading
from selenium.webdriver.common.by import By
import concurrent.futures
from typing import Dict

from tweetfinder import Article

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)

IN_PARALLEL = True  # use this to control if we use parallel threads, or execute serially
POOL_SIZE = 16

# must have a `stories_id` and `url` column in it (we source random_stories for testing from Media Cloud)
#STORY_CSV_FILE = "tweetfinder/test/fixtures/2021-random-stories.csv"
#STORY_CSV_FILE = "tweetfinder/test/fixtures/2020-random-relevant-stories.csv"
STORY_CSV_FILE = "tweetfinder/test/fixtures/tweet_embeds_data.csv"

stories_df = pd.read_csv(STORY_CSV_FILE)
logger.info("Loaded {} random_stories from {}".format(len(stories_df.index), STORY_CSV_FILE))

threadLocal = threading.local()  # lets us save variables on the thread context

start_time = time.time()


def get_driver():
    """
    Manage one chrome instance per thread (so we don't lose time spinning up a chrome per job)
    see: https://stackoverflow.com/questions/53475578/python-selenium-multiprocessing
    :return: A headless chrome web driver we can use to fetch and render webpages
    """
    driver = getattr(threadLocal, 'driver', None)
    if driver is None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
        setattr(threadLocal, 'driver', driver)
    return driver


def count_tweets_goose(html: str) -> int:
    """
    We want to compare our results to Goose, which is what everyone else seems to use.
    :param html: 
    :return: 
    """
    g = Goose()
    my_article = g.extract(raw_html=html)
    tweet_embed_count = len(my_article.tweets)
    return tweet_embed_count


def story_worker(story: Dict) -> Dict:
    """
    Process one story and return the data we can use for comparison
    :param story: one row from the test CSV
    :return: a dict of the info we care about
    """
    try:
        if 'stories_id' in story:
            logger.info("  story {}".format(story['stories_id']))
        data = {}
        url = story['url']
        data['url'] = url
        data['stories_id'] = story['stories_id'] if 'stories_id' in story else ''
        # tweet finder with raw html
        article = Article(url=url, timeout=5)
        data['tweet_finder_embeds'] = article.count_embedded_tweets()
        data['tweet_finder_mentions'] = article.count_mentioned_tweets()
        # tweet finder with JS-rendered html
        driver = get_driver()  # grab the chrome instance for the thread we are in
        driver.get(url)
        time.sleep(1)  # give it a second to render
        rendered_html = driver.find_element(By.TAG_NAME, "html").get_attribute('innerHTML')
        article_js = Article(html=rendered_html)
        data['tweet_finder_js_embeds'] = article_js.count_embedded_tweets()
        data['tweet_finder_js_mentions'] = article_js.count_mentioned_tweets()
        # goose with raw html
        data['goose_embeds'] = count_tweets_goose(article.get_html())
        # goose with JS-rendered html
        data['goose_js_embeds'] = count_tweets_goose(rendered_html)
        # and keep track of the results
        return data
    except Exception:
        # probably a fetch or parse error, so just ignore the story
        return None


results = []

# we tested this in series first, but it was too slow so we support using a pool of threads by default
# (maintaining one chrome instance per thread with a clever hack we found on StackOverflow)
if not IN_PARALLEL:
    for index, s in stories_df.iterrows():
        results.append(story_worker(s))
else:
    # see: https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
    with concurrent.futures.ThreadPoolExecutor(max_workers=POOL_SIZE) as executor:  # using `with` helps ensure cleanup
        futures = [executor.submit(story_worker, story) for _, story in stories_df.iterrows()]
        for future in concurrent.futures.as_completed(futures):
            try:
                story_data = future.result()
                if story_data is not None:  # ignore if fetching/parsing failed
                    results.append(story_data)
            except Exception as exc:
                logger.exception(exc)

# keep track of how long it took so we can compare performance
end_time = time.time()
elapsed_secs = end_time - start_time
logger.info("Took {} seconds total for {} stories ({} threads)".format(elapsed_secs, len(stories_df.index), POOL_SIZE))

# Save results to a time-stamped CSV so we can review and share them without confusion about different runs
story_tester_df = pd.DataFrame.from_dict(results)
output_filename = 'evaluation-results-{}.csv'.format(time.strftime("%Y%m%d-%H%M%S"))
story_tester_df.to_csv(output_filename, index=False)
logger.info("Wrote results to {}".format(output_filename))
