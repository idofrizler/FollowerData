TWITTER_URL_PREFIX = 'https://api.twitter.com/2/'


def create_url_user_tweets(user_id, pagination_token=None):
    search_url = '{}users/{}/tweets'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {
        'tweet.fields': 'id,author_id,public_metrics,created_at,in_reply_to_user_id,conversation_id',
        'exclude': 'retweets',
        'max_results': 100,
        'pagination_token': pagination_token}
    return search_url, query_params


def create_url_liking_users(tweet_id, pagination_token=None):
    search_url = '{}tweets/{}/liking_users'.format(TWITTER_URL_PREFIX, tweet_id)
    query_params = {
        'user.fields': 'id,name,username',
        'pagination_token': pagination_token
    }
    return search_url, query_params


def create_url_user_information(user_id):
    search_url = '{}users/{}'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {'user.fields': 'created_at,id,username,name,description,pinned_tweet_id,public_metrics,verified'}
    return search_url, query_params


def create_url_user_by_username(user_alias):
    search_url = '{}users/by/username/{}'.format(TWITTER_URL_PREFIX, user_alias)
    query_params = {}
    return search_url, query_params


def create_url_tweet_public_metrics(tweet_id):
    search_url = '{}tweets/{}'.format(TWITTER_URL_PREFIX, tweet_id)
    query_params = {'tweet.fields': 'public_metrics,author_id'}
    return search_url, query_params


def create_url_user_followers(user_id, pagination_token=None):
    search_url = '{}users/{}/followers'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {
        'pagination_token': pagination_token
    }
    return search_url, query_params


def create_url_user_following(user_id, pagination_token=None):
    search_url = '{}users/{}/following'.format(TWITTER_URL_PREFIX, user_id)
    query_params = {
        'pagination_token': pagination_token
    }
    return search_url, query_params
