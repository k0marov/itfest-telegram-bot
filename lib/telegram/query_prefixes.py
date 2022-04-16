"""Module that provides the callback prefix constants and helper functions operating them"""
from lib.core.topics import Topic, get_topic_by_id


TOPIC_INFO_PREFIX = "info___"
TOPIC_SUBSCRIBE_PREFIX = "sub___"
TOPIC_UNSUBSCRIBE_PREFIX = "unsub___"
TOPIC_LAST_POSTS_PREFIX = "posts___"

def create_topic_query(topic: Topic, prefix: str): 
    """creates query from topic and prefix"""
    return prefix + topic.id 

def get_topic_from_query(query: str) -> Topic:
    """returns topic that was inserted into the query"""
    topic_id = query.split("___")[-1]
    return get_topic_by_id(topic_id)

def is_query_with_prefix(query: str, prefix: str):
    """returns true if it is a query with the given prefix and false otherwise"""
    return query.startswith(prefix)
