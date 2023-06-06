# =============================================================================
# Tweet NER Annotation
# =============================================================================
#
# Helper functions for Flair NER annotation of tweet data.
#
from datetime import datetime


def format_tweet(tweet_data: dict) -> dict:
    array_fields = [
        "links",
        "domains",
        "media_urls",
        "media_files",
        "media_types",
        "media_alt_texts",
        "mentioned_names",
        "mentioned_ids",
        "hashtags",
    ]
    for field in array_fields:
        if tweet_data.get(field):
            tweet_data[field] = tweet_data[field].split("|")
        else:
            tweet_data[field] = []
    integer_fields = [
        "retweet_count",
        "like_count",
        "reply_count",
        "impression_count",
        "user_tweets",
        "user_followers",
        "user_friends",
        "user_likes",
        "user_lists",
    ]
    for field in integer_fields:
        if tweet_data.get(field):
            tweet_data[field] = int(tweet_data[field])
    boolean_fields = ["possibly_sensitive", "user_verified", "match_query"]
    for field in boolean_fields:
        if tweet_data.get(field) == 0:
            tweet_data[field] = False
        elif tweet_data.get(field) == 1:
            tweet_data[field] = False
    timestamp_fields = [
        "timestamp_utc",
        "user_timestamp_utc",
        "retweet_timestamp_utc",
        "quoted_timestamp_utc",
    ]
    for field in timestamp_fields:
        if tweet_data.get(field):
            tweet_data[field] = str(datetime.fromtimestamp(int(tweet_data[field])))
    datetime_fields = [
        "local_time",
        "user_created_at",
    ]
    for field in datetime_fields:
        if tweet_data.get(field):
            tweet_data[field] = str(
                datetime.strptime(tweet_data[field], "%Y-%m-%dT%H:%M:%S")
            )
    if tweet_data.get("collection_time"):
        tweet_data["collection_time"] = str(
            datetime.strptime(tweet_data["collection_time"], "%Y-%m-%dT%H:%M:%S.%f")
        )
    for k, v in tweet_data.items():
        if v == "":
            tweet_data[k] = None
    tweet_data["_id"] = tweet_data["id"]
    return tweet_data
