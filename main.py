import logging

import api
import kusto_handler

USER_ALIAS = '<your_user_alias; no @ needed>'
logging.basicConfig(format='%(asctime)s %(levelname)-5s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').disabled = True


def handle_user_information(user_id):
    user_info = api.get_user_information(user_id)
    user_info_data = user_info['data']
    kusto_handler.insert_user_to_database(user_info_data)

    return user_info_data


def handle_followers(user_id, user_info_data):
    pagination_token = 'FIRST_RUN'
    followers = api.get_user_followers(user_id)

    while pagination_token:
        followers_data = followers['data']
        logging.info('Queried {} followers records from Twitter'.format(len(followers_data)))
        kusto_handler.insert_followers_to_database(user_info_data, followers_data, followers=True)

        for follower in followers_data:
            handle_user_information(follower['id'])

        pagination_token = followers['meta'].get('next_token', None)
        if pagination_token:
            followers = api.get_user_followers(user_id, pagination_token)


def handle_following(user_id, user_info_data):
    pagination_token = 'FIRST_RUN'
    following = api.get_user_following(user_id)

    while pagination_token:
        following_data = following['data']
        logging.info('Queried {} following records from Twitter'.format(len(following_data)))
        kusto_handler.insert_followers_to_database(user_info_data, following_data, followers=False)

        for following_user in following_data:
            handle_user_information(following_user['id'])

        pagination_token = following['meta'].get('next_token', None)
        if pagination_token:
            following = api.get_user_following(user_id, pagination_token)


def handle_liking_users(tweet_id, user_info_data):
    pagination_token = 'FIRST_RUN'
    liking_users = api.get_liking_users_for_tweet(tweet_id)

    while pagination_token and 'data' in liking_users:
        liking_users_data = liking_users['data']
        logging.info('Queried {} new liking user records from Twitter'.format(len(liking_users_data)))
        kusto_handler.insert_likes_to_database(liking_users_data, tweet_id, user_info_data)

        pagination_token = liking_users['meta'].get('next_token', None)
        if pagination_token:
            liking_users = api.get_liking_users_for_tweet(tweet_id, pagination_token)


def handle_tweets_and_liking_users(user_id, user_info_data):
    pagination_token = 'FIRST_RUN'
    tweets = api.get_user_tweets(user_id)

    while pagination_token:
        tweets_data = tweets['data']
        logging.info('Queried {} new tweets from Twitter'.format(len(tweets_data)))
        kusto_handler.insert_tweets_to_database(tweets_data)

        for tweet in tweets_data:
            tweet_id = tweet['id']
            handle_liking_users(tweet_id, user_info_data)

        pagination_token = tweets['meta'].get('next_token', None)
        if pagination_token:
            tweets = api.get_user_tweets(user_id, pagination_token)


def get_data(user_id):

    user_info_data = handle_user_information(user_id)
    handle_followers(user_id, user_info_data)
    handle_following(user_id, user_info_data)
    handle_tweets_and_liking_users(user_id, user_info_data)

    #     for user in liking_users:
    #         liking_user_id = user['data']['id']
    #         liking_user_public_metrics = api.get_user_public_metrics(liking_user_id)
    #         kusto_handler.insert_user_to_database(liking_user_public_metrics)


def get_user_id(user_alias):
    user_data = api.get_user_by_username(user_alias)
    user_id = user_data['data']['id']
    logging.info('User ID for {} is {}'.format(user_alias, user_id))
    return user_id


if __name__ == '__main__':
    derived_user_id = get_user_id(USER_ALIAS)
    get_data(derived_user_id)
