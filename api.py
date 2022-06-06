import os
import requests
from time import sleep

import urls


def get_twitter_token():
    return os.environ['TwitterToken']


def create_headers():
    twitter_token = get_twitter_token()
    return {"Authorization": "Bearer {}".format(twitter_token)}


headers = create_headers()


def connect_to_endpoint(url, params):
    response = requests.request('GET', url, headers=headers, params=params)

    while response.status_code == 429:  # Rate limiting
        print('Rate limit reached; sleeping for 5 minutes')
        sleep(300)  # Sleep for 5 minutes and try again
        response = requests.request('GET', url, headers=headers, params=params)

    if response.status_code not in (200, 201):
        raise Exception(response.status_code, response.text)

    return response.json()


def get_user_tweets(user_id, pagination_token=None):
    url, params = urls.create_url_user_tweets(user_id, pagination_token)
    tweets = connect_to_endpoint(url, params)
    return tweets


def get_liking_users_for_tweet(tweet_id, pagination_token=None):
    url, params = urls.create_url_liking_users(tweet_id, pagination_token)
    liking_users = connect_to_endpoint(url, params)
    return liking_users


def get_user_information(user_id):
    url, params = urls.create_url_user_information(user_id)
    user_info = connect_to_endpoint(url, params)
    return user_info


def get_user_by_username(user_alias):
    url, params = urls.create_url_user_by_username(user_alias)
    user_data = connect_to_endpoint(url, params)
    return user_data


def get_tweet_info(tweet_id):
    url, params = urls.create_url_tweet_public_metrics(tweet_id)
    public_metrics = connect_to_endpoint(url, params)
    return public_metrics


def get_user_followers(user_id, pagination_token=None):
    url, params = urls.create_url_user_followers(user_id, pagination_token)
    followers = connect_to_endpoint(url, params)
    return followers


def get_user_following(user_id, pagination_token=None):
    url, params = urls.create_url_user_following(user_id, pagination_token)
    following = connect_to_endpoint(url, params)
    return following
