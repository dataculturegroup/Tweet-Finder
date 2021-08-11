import os

module_dir = os.path.dirname(os.path.abspath(__file__))

# phrases we found to be mentions of tweets or tweet activity from scanning articles ourselves
BASIC = ['tweeted', 'to twitter', 'tweets', 'tweeting', 'retweet', 'in a tweet', 'to tweet', 'tweet from',
         'wrote on twitter', 'said on twitter', 'from a tweet']

# twitter phrases from https://arxiv.org/abs/1810.13078
with open(os.path.join(module_dir, "data", "twitter-patterns-rony-2018.txt"), "r") as rony_2018_file:
    RONY_2018 = rony_2018_file.readlines()

# twitter phrases from https://www.tandfonline.com/doi/full/10.1080/1369118X.2021.1874037
MOLYNEUX_2020 = ['retweet', 'according to a tweet']

ALL = set(BASIC + RONY_2018 + MOLYNEUX_2020)
