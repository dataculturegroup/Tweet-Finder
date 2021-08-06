import json
import os
import pandas as pd
from tweetfinder import Article

trunk = './random_stories/stories/stories'

tweet_id_list = []
embedded_tweet_count_list = []
ref_tweet_count = []
has_embed_list = []
has_ref_list = []
for file in os.listdir(trunk):
    f = os.path.join(trunk, file)
    with open(f) as filename:
        article_json = json.load(filename)
    article = Article(html=article_json['story_text'])
    tweet_id_list.append(article_json['story_id'])
    embedded_tweet_count_list.append(article.count_embedded_tweets())
    ref_tweet_count.append(article.count_referenced_tweets())
    has_embed_list.append(article.embeds_tweets())
    has_ref_list.append(article.references_tweets())

story_tester_df = pd.DataFrame({
    'tweet_id': tweet_id_list,
    'embedded_tweet_count': embedded_tweet_count_list,
    'ref_tweet_count': ref_tweet_count,
    'has_embeds': has_embed_list,
    'has_refs': has_ref_list
})
