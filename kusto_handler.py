import logging
from datetime import datetime

import pandas
from azure.kusto.data import KustoConnectionStringBuilder, DataFormat, KustoClient
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties

KUSTO_URI = "https://<your_kusto_cluster>.kusto.windows.net/"
KUSTO_INGEST_URI = "https://ingest-<your_kusto_cluster>.kusto.windows.net/"
KUSTO_DATABASE = "FollowerData"

KCSB_INGEST = KustoConnectionStringBuilder.with_interactive_login(KUSTO_INGEST_URI)
KCSB_INGEST.authority_id = 'organizations'
KCSB_DATA = KustoConnectionStringBuilder.with_interactive_login(KUSTO_URI)
KCSB_DATA.authority_id = 'organizations'

TWEETS_TABLE = "Tweets"
USERS_TABLE = "Users"
FOLLOWS_TABLE = "Follows"
LIKES_TABLE = "Likes"
INGESTION_CLIENT = QueuedIngestClient(KCSB_INGEST)
DATA_CLIENT = KustoClient(KCSB_DATA)


def cache_user_records_from_kusto():
    query = "{} | distinct UserId".format(USERS_TABLE)
    response = DATA_CLIENT.execute_query(KUSTO_DATABASE, query)
    df = dataframe_from_result_table(response.primary_results[0])
    records = df.to_dict('records')
    return set([str(r['UserId']) for r in records])


cached_user_records = cache_user_records_from_kusto()


def insert_user_to_database(user_info):
    user_id = user_info['id']
    if user_id in cached_user_records:
        logging.info('{} already exists in Users table; skipping'.format(user_id))
        return

    fields = ['IngestTimestamp', 'CreatedTimestamp', 'UserId', 'UserAlias', 'UserPrettyName', 'Bio', 'PinnedTweetId',
              'Followers', 'Following', 'Tweets', 'IsVerified']
    user_data = UserData(user_info)
    rows = [user_data.to_list()]

    df = pandas.DataFrame(data=rows, columns=fields)

    ing_prop = IngestionProperties(database=KUSTO_DATABASE, table=USERS_TABLE, data_format=DataFormat.CSV)
    INGESTION_CLIENT.ingest_from_dataframe(df, ingestion_properties=ing_prop)
    cached_user_records.add(user_id)
    logging.info('Ingested user information @{} to Kusto'.format(user_data.user_alias))


def insert_tweets_to_database(tweets):
    fields = ['IngestTimestamp','TweetTimestamp','TweetId','AuthorId','ConversationId','InReplyTo','Text','Likes','Comments']
    rows = []
    for tweet in tweets:
        rows.append(TweetData(tweet).to_list())

    df = pandas.DataFrame(data=rows, columns=fields)

    ing_prop = IngestionProperties(database=KUSTO_DATABASE, table=TWEETS_TABLE, data_format=DataFormat.CSV)
    INGESTION_CLIENT.ingest_from_dataframe(df, ingestion_properties=ing_prop)
    logging.info('Ingested {} tweets to Kusto'.format(len(tweets)))


def insert_followers_to_database(user_info, user_list, followers):
    fields = ['IngestTimestamp', 'FollowingUserId', 'FollowingUserAlias', 'FollowingUserPrettyName', 'FollowedUserId',
              'FollowedUserAlias', 'FollowedUserPrettyName']
    rows = []
    for user in user_list:
        if followers:
            rows.append(FollowerData(user, user_info).to_list())
        else:
            rows.append(FollowerData(user_info, user).to_list())

    df = pandas.DataFrame(data=rows, columns=fields)

    ing_prop = IngestionProperties(database=KUSTO_DATABASE, table=FOLLOWS_TABLE, data_format=DataFormat.CSV)
    INGESTION_CLIENT.ingest_from_dataframe(df, ingestion_properties=ing_prop)
    logging.info('Ingested {} follows to Kusto'.format(len(user_list)))


def insert_likes_to_database(liking_users, tweet_id, author_info):
    fields = ['IngestTimestamp', 'LikingUserId', 'LikingUserAlias', 'LikingUserPrettyName', 'TweetId', 'AuthorId',
              'AuthorAlias', 'AuthorPrettyName']
    rows = []
    for user in liking_users:
        rows.append(LikeData(user, tweet_id, author_info).to_list())

    df = pandas.DataFrame(data=rows, columns=fields)

    ing_prop = IngestionProperties(database=KUSTO_DATABASE, table=LIKES_TABLE, data_format=DataFormat.CSV)
    INGESTION_CLIENT.ingest_from_dataframe(df, ingestion_properties=ing_prop)
    logging.info('Ingested {} liking users to Kusto'.format(len(liking_users)))


class UserData(object):
    def __init__(self, user_obj):
        self.ingest_time = datetime.utcnow()
        self.created_at = user_obj.get('created_at', '')
        self.id = user_obj.get('id', '')
        self.user_alias = user_obj.get('username', '')
        self.pretty_name = user_obj.get('name', '')
        self.bio = user_obj.get('description', '')
        self.pinned_tweet_id = user_obj.get('pinned_tweet_id', '')
        self.followers_count = user_obj.get('public_metrics', {}).get('followers_count', 0)
        self.following_count = user_obj.get('public_metrics', {}).get('following_count', 0)
        self.tweet_count = user_obj.get('public_metrics', {}).get('tweet_count', 0)
        self.verified = user_obj.get('verified', False)

    def to_list(self):
        return [self.ingest_time, self.created_at, self.id, self.user_alias, self.pretty_name, self.bio,
                self.pinned_tweet_id, self.followers_count, self.following_count, self.tweet_count, self.verified]


class TweetData(object):
    def __init__(self, tweet_obj):
        self.ingest_time = datetime.utcnow()
        self.created_at = tweet_obj.get('created_at', '')
        self.id = tweet_obj.get('id', '')
        self.author_id = tweet_obj.get('author_id', '')
        self.conversation_id = tweet_obj.get('conversation_id', '')
        self.in_reply_to_user_id = tweet_obj.get('in_reply_to_user_id', '')
        self.text = tweet_obj.get('text', '')
        self.like_count = tweet_obj.get('public_metrics', {}).get('like_count', 0)
        self.reply_count = tweet_obj.get('public_metrics', {}).get('reply_count', 0)

    def to_list(self):
        return [self.ingest_time, self.created_at, self.id, self.author_id, self.conversation_id,
                self.in_reply_to_user_id, self.text, self.like_count, self.reply_count]


class FollowerData(object):
    def __init__(self, following_obj, followed_obj):
        self.ingest_time = datetime.utcnow()
        self.following_id = following_obj.get('id', '')
        self.following_user_alias = following_obj.get('username', '')
        self.following_pretty_name = following_obj.get('name', '')
        self.followed_id = followed_obj.get('id', '')
        self.followed_user_alias = followed_obj.get('username', '')
        self.followed_pretty_name = followed_obj.get('name', '')

    def to_list(self):
        return [self.ingest_time, self.following_id, self.following_user_alias, self.following_pretty_name,
                self.followed_id, self.followed_user_alias, self.followed_pretty_name]


class LikeData(object):
    def __init__(self, liking_user_obj, tweet_id, author_info_obj):
        self.ingest_time = datetime.utcnow()
        self.liking_user_id = liking_user_obj.get('id', '')
        self.liking_user_alias = liking_user_obj.get('username', '')
        self.liking_user_pretty_name = liking_user_obj.get('name', '')
        self.tweet_id = tweet_id
        self.author_id = author_info_obj.get('id', '')
        self.author_alias = author_info_obj.get('username', '')
        self.author_pretty_name = author_info_obj.get('name', '')

    def to_list(self):
        return [self.ingest_time, self.liking_user_id, self.liking_user_alias, self.liking_user_pretty_name,
                self.tweet_id, self.author_id, self.author_alias, self.author_pretty_name]
