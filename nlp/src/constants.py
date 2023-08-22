BODY = {"settings": {"index": {"number_of_shards": 4}}}

TWEET_STANZA_MAPPINGS = {
    "properties": {
        # -------------------------- #
        # INPUT DATA FIELDS
        "query": {"type": "keyword"},
        "id": {"type": "keyword"},
        "timestamp_utc": {"type": "date"},
        "local_time": {"type": "date"},
        "user_screen_name": {"type": "keyword"},
        "text": {"type": "text"},
        "possibly_sensitive": {"type": "boolean"},
        "retweet_count": {"type": "integer"},
        "like_count": {"type": "integer"},
        "reply_count": {"type": "integer"},
        "impression_count": {"type": "integer"},
        "lang": {"type": "keyword"},
        "to_username": {"type": "keyword"},
        "to_userid": {"type": "keyword"},
        "to_tweetid": {"type": "keyword"},
        "source_name": {"type": "keyword"},
        "source_url": {"type": "keyword"},
        "user_location": {"type": "text"},
        "lat": {"type": "float"},
        "lng": {"type": "float"},
        "user_id": {"type": "keyword"},
        "user_name": {"type": "keyword"},
        "user_verified": {"type": "boolean"},
        "user_description": {"type": "text"},
        "user_url": {"type": "text"},
        "user_image": {"type": "text"},
        "user_tweets": {"type": "integer"},
        "user_followers": {"type": "integer"},
        "user_friends": {"type": "integer"},
        "user_likes": {"type": "integer"},
        "user_lists": {"type": "integer"},
        "user_created_at": {"type": "date"},
        "user_timestamp_utc": {"type": "date"},
        "collected_via": {"type": "keyword"},
        "match_query": {"type": "boolean"},
        "retweeted_id": {"type": "keyword"},
        "retweeted_user": {"type": "keyword"},
        "retweeted_user_id": {"type": "keyword"},
        "retweeted_timestamp_utc": {"type": "date"},
        "quoted_id": {"type": "keyword"},
        "quoted_user": {"type": "keyword"},
        "quoted_user_id": {"type": "keyword"},
        "quoted_timestamp_utc": {"type": "date"},
        "collection_time": {"type": "date"},
        "url": {"type": "text"},
        "place_country_code": {"type": "keyword"},
        "place_name": {"type": "text"},
        "place_type": {"type": "keyword"},
        "place_coordinates": {"type": "text"},
        "links": {"type": "text"},
        "domains": {"type": "keyword"},
        "media_urls": {"type": "text"},
        "media_files": {"type": "text"},
        "media_types": {"type": "keyword"},
        "media_alt_texts": {"type": "text"},
        "mentioned_names": {"type": "keyword"},
        "mentioned_ids": {"type": "keyword"},
        "hashtags": {"type": "keyword"},
        # -------------------------- #
        # STANZA ANNOTATIONS
        "dependencies": {"type": "nested"},
        "sentences": {"type": "nested"},
    }
}


COREF_MAPPINGS = TWEET_STANZA_MAPPINGS.copy()
# COREF_MAPPINGS["properties"].update({
#     ""
# })
