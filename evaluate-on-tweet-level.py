import time
from goose3 import Goose
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

from tweetfinder import Article

answer_dict = {'https://www.techradar.com/news/lord-of-the-rings-on-amazon' : ['1349403885836791808',
                                                                               '1422255647106617359',
                                                                               '1422618263695941633',
                                                                               '1103656820130775050',
                                                                               '1410622923421851649'],
               'https://edition.cnn.com/2021/05/12/football/mo-salah-tweet-riyad-mahrez-benjamin-mendy-spt-intl/index.html':
               ['1392185890844430342', '1392187739383255051', '1391714799717953536', '1391436786665246726', '1392185890844430342'],
               'https://www.foxnews.com/politics/black-lives-matter-hamas-terrorists-israeli': ['1394289672101064704',
                                                                                                '1394578742920552453',
                                                                                                '1394667705173688326'],
               'https://www.breitbart.com/economy/2021/03/03/washington-post-editorial-board-15-minimum-wage-will-not-happen/?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+breitbart+%28Breitbart+News%29':
               ['1366545099132456961', '1366922134057058304', '1366837187094978566'],
               'https://www.foxnews.com/us/new-jersey-house-party-shooting-dead-injured-state-police-suspect':
                   ['1396471486651768837', '1396472421641822209'],
               'https://www.foxnews.com/us/us-seeing-wave-of-textbook-anti-semitism-amid-israel-gaza-tensions':
               ['1395469376849993730', '1395094581255966723'],
               'https://www.npr.org/2021/05/25/1000129271/marjorie-taylor-greenes-holocaust-remarks-blasted-by-republicans-leaders':
               ['1397192128598523911', '1396805268126720001'],
               'https://www.cbsnews.com/news/alexei-navalny-russia-putin-critic-prison-health-infirmary-arrests/':
               ['1379075608030892032', '1379408844984569860'],
               'https://www.foxnews.com/us/fox-news-spots-migrant-group-running-across-southern-border-into-us':
               ['1396528462026924033'],
               'https://www.vice.com/en/article/wx8wm5/arkansas-just-became-the-first-state-to-ban-health-care-for-trans-kids':
               ['1379510072716488715'],
               'https://www.cnn.com/us/live-news/san-jose-ca-shooting-05-26-21/h_41658163e6c6f2416d346adb6c01119f':
               ['1397580228537450510'],
               'https://www.cbsnews.com/news/texas-defund-police-bill-abbott/':
               ['1396643982785105920'],
               'https://newrepublic.com/article/161084/republican-retreat-governance-voter-suppression':
               ['1354556580231077891'],
               'https://www.cnn.com/2021/05/17/investing/bitcoin-price-elon-musk-tesla-intl-hnk/index.html':
              ['1394001894809427971'],
              'https://www.cbsnews.com/news/rand-paul-suspicious-package-white-powder/':
              ['1396973910994915328'],
               'https://boston.cbslocal.com/2021/05/26/boston-dorchester-fire-fayston-street-homes-burning/':
               ['1397609773898600450'],
               'https://www.msnbc.com/opinion/texas-new-abortion-law-isn-t-just-dangerous-it-s-n1267950':
               ['1394730325612404741'],
               'https://www.bbc.com/news/world-europe-57250285':
               ['1396719090321010688'],
               'https://www.npr.org/2021/05/21/999020140/its-now-legal-to-practice-yoga-in-alabamas-public-schools':
               ['1395482631043702787'],
               'https://www.msnbc.com/opinion/republicans-say-court-packing-unconstitutional-they-re-wrong-n1265972':
               ['1387966124797661188']}


def getDriver():
    # setup a headless chrome we can re-use it in all the tests within this class
    chrome_options = Options()
    chrome_options.add_argument('--mute-audio')
    chrome_options.add_argument('--headless')
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    except WebDriverException as wde:
        driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
    return driver


def _loadViaSelenium(driver, url: str, delay_secs: int = 1):
    driver.get(url)
    # let it render the javascript, then grab the *rendered* html, not the source_html
    time.sleep(delay_secs)  # hopefully it renders after this much time
    rendered_html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
    # now that we have HTML rendered by Javascript, we can check for tweets
    return Article(html=rendered_html)


def count_tweets_goose(url):
    g = Goose()
    article = g.extract(url=url)
    return article.tweets


def count_tweets_goose_js(html):
    g = Goose()
    article = g.extract(raw_html=html)
    return article.tweets


def get_stats_for_all():
    """
    Pull the total cumulative scores. Notes:
    * True Positive: tweet id in manual set and also in set from tweetfinder
    * False Positive: tweet id not manual set but is in set from tweetfinder
    * False Negative: tweet id in manual set and not in set from tweetfinder
    :return:
    """
    count_dict = {'tweetfinder': {'tp': 0, 'fp': 0},
                  'tweetfinder_js': {'tp': 0, 'fp': 0},
                  'goose': {'tp': 0, 'fp': 0},
                  'goose_js': {'tp': 0, 'fp': 0}
                  }
    driver = getDriver()
    for url, tweet_id_list in answer_dict.items():
        article_js = _loadViaSelenium(driver, url)
        article = Article(url=url)
        found_tweets_tweetfinder = article.list_embedded_tweets()
        found_tweets_goose = count_tweets_goose(url)
        found_tweets_tweetfinder_js = article_js.list_embedded_tweets()
        found_tweets_goose_js = count_tweets_goose_js(article_js.get_html())
        found_id_dict = {'tweetfinder': found_tweets_tweetfinder, 'tweetfinder_js': found_tweets_tweetfinder_js,
                         'goose': found_tweets_goose, 'goose_js': found_tweets_goose_js}
        for key, found_tweets in found_id_dict.items():
            found_tweets = found_id_dict[key]
            key_count_dict = count_dict[key]
            if key == 'tweetfinder' or key == 'tweetfinder_js':
                found_id_list = []
                for tweet in found_tweets:
                    found_id_list.append(tweet['tweet_id'])
                found_tweets = found_id_list
            for tweet_id in found_tweets:
                if key == 'goose':
                    id_start = tweet_id.find('status/')
                    tweet_id = tweet_id[id_start + 7 :id_start + 26]
                if tweet_id in tweet_id_list:
                    key_count_dict['tp'] += 1
                else:
                    key_count_dict['fp'] += 1
    total_count = 36
    stats_dict = {}
    stats_dict_dict = {}
    for key in count_dict.keys():
        try:
            count_dict_key = count_dict[key]
            tp = count_dict_key['tp']
            fp = count_dict_key['fp']
            fn = total_count - tp
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
        except ZeroDivisionError:
            precision = 0
            recall = 0
        stats_dict_dict[key] = {'precision': precision, 'recall': recall}
        stats_dict[key] = [stats_dict_dict[key]['precision'], stats_dict_dict[key]['recall']]
    eval_df = pd.DataFrame(stats_dict)
    eval_df.to_csv('embeds_tweet_review.csv', index=False)


if __name__ == "__main__":
    get_stats_for_all()



