"""Module that provides the Vk class"""
import datetime
from typing import List
import vk

from lib.core.post import Post
import lib.core.topics as topics
import lib.core.config as config

class Vk:
    """Class that provides access to the Vkontakte API"""
    api_version = "5.131"
    def __init__(self, token):
        self.token = token
        self.session = vk.Session(access_token=token)
        self.api = vk.API(self.session)
    def get_group_avatar(self, topic: topics.Topic) -> str:
        """Returns the url avatar of the vk group corresponding to the given topic"""
        return self.api.groups.getById(group_id=topic.vk_str_id, v=self.api_version)[0]['photo_200']
    def get_posts_for_last_n_minutes(self, topic: topics.Topic, minutes: int) -> List[Post]:
        """Gets posts (that are not older than the given minutes value)
        from the vk group corresponding to the given topic"""
        posts = self.get_last_n_posts(topic, config.VK_POSTS_TO_CHECK_PERIODICALLY)
        max_diff = datetime.timedelta(minutes=minutes)
        return [post for post in posts
            if datetime.datetime.now(datetime.timezone.utc) - post.date < max_diff
        ]
    def get_last_n_posts(self, topic: topics.Topic, n_posts: int) -> List[Post]:
        """Gets the given number of most recent posts from the given topic group"""
        response = self.api.wall.get(domain=topic.vk_str_id, count=n_posts, v=self.api_version)
        result = []
        # parse responses
        for outer_post in response['items']:
            # handling reposts
            if outer_post.get('copy_history'):
                post = outer_post['copy_history'][-1]
            else:
                post = outer_post

            date = datetime.datetime.fromtimestamp(post['date'], tz=datetime.timezone.utc)
            text = post['text']
            if topic.vk_str_id == topics.BASE_TOPIC_STR_ID and not topic.hashtag in text:
                continue
            photos = []
            for attachment in post['attachments']:
                if attachment['type'] == "photo":
                    photos.append(attachment['photo']['sizes'][-1]['url'])

            result.append(Post(text, photos, topic, post['id'], date))
        return result
