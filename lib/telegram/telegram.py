"""Module that contains the Telegram class"""
from typing import Callable, List
from dataclasses import dataclass
from telegram import CallbackQuery
from telegram import Bot as TelegramBot

from lib.telegram.telegram_input import TelegramInput, TelegramInputCallbacks
from lib.telegram.telegram_output import TelegramOutput
from lib.core.post import Post
import lib.core.topics as topics
import lib.core.config as config


@dataclass(frozen=True)
class TelegramCallbacks:
    """Callbacks for the Telegram class"""
    subscribe: Callable[[str, topics.Topic], None]
    unsubscribe: Callable[[str], topics.Topic]
    is_subscribed: Callable[[str, topics.Topic], bool]
    get_group_avatar: Callable[[topics.Topic], str]
    get_last_posts: Callable[[topics.Topic], List[Post]]

class Telegram:
    """Class that connects the TelegramInput and TelegramOutput classes,
    also calling passed in callbacks to read/write external data"""
    def __init__(self, token: str, callbacks: TelegramCallbacks):
        self.callbacks = callbacks
        self.bot = TelegramBot(token=token)
        self.output = TelegramOutput(self.bot)
        self.input = TelegramInput(self.bot, TelegramInputCallbacks(
            on_start=self.output.display_start,
            on_info=self.output.display_info,
            on_contacts=self.output.display_contacts,
            on_choose_last_posts=self.output.choose_topic_for_last_posts,
            on_topics=self.__on_topics,
            on_get_last_posts_query=self.__on_get_last_posts_query,
            on_topic_info_query=self.__on_topic_info_query,
            on_subscribe_query=self.__on_subscribe_query,
            on_unsubscribe_query=self.__on_unsubscribe_query
        ))
    def start_bot(self) -> None:
        """Starts the telegram bot"""
        self.input.start_updater()
    def display_posts_for_users(self, posts: List[Post], users: List[str]) -> None:
        """Displays given posts to each of the given users"""
        self.output.display_posts_for_users(posts=posts, users=users)

    def __on_topics(self, chat_id: str):
        is_subscribed = lambda topic: self.callbacks.is_subscribed(topic=topic, user_id=chat_id)
        self.output.display_topics_list(chat_id, is_subscribed)
    def __on_get_last_posts_query(self, query: CallbackQuery, chat_id: str, topic: topics.Topic):
        post_list = self.callbacks.get_last_posts(topic, config.LAST_POSTS_COMMAND_COUNT)
        self.output.answer_get_last_posts_query(
            query=query,
            chat_id=chat_id,
            topic=topic,
            post_list=post_list
        )
    def __on_topic_info_query(self, query: CallbackQuery, chat_id: str, topic: topics.Topic):
        photo_url = self.callbacks.get_group_avatar(topic)
        is_subscribed = self.callbacks.is_subscribed(chat_id, topic)
        self.output.answer_topic_info_query(query, chat_id, topic, photo_url, is_subscribed)
    def __on_subscribe_query(self, query: CallbackQuery, chat_id: str, topic: topics.Topic):
        self.callbacks.subscribe(chat_id, topic)
        self.output.answer_subscribe_query(
            query=query,
            topic=topic
        )
    def __on_unsubscribe_query(self, query: CallbackQuery, chat_id: str, topic: topics.Topic):
        self.callbacks.unsubscribe(chat_id, topic)
        self.output.answer_unsubscribe_query(
            query=query,
            topic=topic
        )
