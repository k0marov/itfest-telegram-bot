"""Module that provides the Post class"""
import datetime
from typing import List
from dataclasses import dataclass
import lib.core.topics as topics

@dataclass(frozen=True)
class Post:
    """A class representing a post, can contain photo urls"""
    text: str
    photos: List[str]
    topic: topics.Topic
    post_id: str
    date: datetime.datetime
    def get_vk_link(self):
        """Returns the link to the vk post"""
        return f'vk.com/{self.topic.vk_str_id}?w=wall-{self.topic.vk_num_id}_{self.post_id}'
