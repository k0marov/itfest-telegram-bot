"""Module that provides the TelegramOutput class"""
import time
from typing import Callable, List, Union
from telegram import (
    ParseMode, 
    Bot as TelegramBot,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    ReplyKeyboardMarkup
)
from telegram.error import TelegramError
from lib.core.post import Post
import lib.core.messages as messages
import lib.core.topics as topics
import lib.telegram.query_prefixes as query_prefixes

class TelegramOutput:
    """Class that handles output (e.g sending messages to users) to Telegram"""
    def __init__(self, bot_instance: TelegramBot):
        self.bot = bot_instance
    def display_posts_for_users(self, posts: List[Post], users: List[str]):
        """Displays all given posts for each of the given users"""
        for user_id in users:
            for post in posts:
                self.__display_post(post=post, chat_id=user_id)
                time.sleep(1)
    def display_start(self, chat_id):
        """Displays the start message + command buttons"""
        text = messages.START_MESSAGE
        commands = [
            [messages.TOPICS_COMMAND],
            [messages.INFO_COMMAND, messages.CONTACTS_COMMAND],
            [messages.LAST_POSTS_COMMAND]
        ]
        self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=ReplyKeyboardMarkup(commands)
        )
    def display_topics_list(
        self,
        chat_id: str,
        is_topic_subscribed: Callable[[topics.Topic], bool]
    ):
        """Displays a list of all topics
        where if you click on a topic you get info about it"""
        topic_to_button = lambda topic: InlineKeyboardButton(
            text=topic.hashtag + (" ✅️" if is_topic_subscribed(topic) else ""),
            callback_data=query_prefixes.create_topic_query(topic, query_prefixes.TOPIC_INFO_PREFIX)
        )
        self.__internal_topic_list(chat_id, messages.TOPICS_TEXT, topic_to_button)

    def choose_topic_for_last_posts(self, chat_id):
        """Displays a list of all topics
        where if you click on topic you get it's last posts"""
        topic_to_button = lambda topic: InlineKeyboardButton(
            text=topic.hashtag,
            callback_data=
                query_prefixes.create_topic_query(topic, query_prefixes.TOPIC_LAST_POSTS_PREFIX)
        )
        self.__internal_topic_list(chat_id, messages.LAST_POSTS_TOPICS_TEXT, topic_to_button)
    def display_info(self, chat_id):
        """Displays info about commands"""
        self.bot.send_message(
            chat_id=chat_id,
            text=messages.COMMAND_INFO_TEXT, 
            parse_mode=ParseMode.HTML
        )
    def display_contacts(self, chat_id):
        """Displays contact data"""
        self.bot.send_message(
            chat_id=chat_id,
            text=messages.CONTACTS_TEXT,
        )
    def answer_get_last_posts_query(self,
        query: CallbackQuery,
        chat_id: str,
        topic: topics.Topic,
        post_list: List[Post]
    ):
        """Displays last posts of a topic (activated when clicked on a button)"""
        self.__answer_query(
            query=query,
            answer_text=None,
            edit_text=messages.SELECTED_TEXT + " " + topic.hashtag
        )
        self.display_posts_for_users(posts=post_list, users=[chat_id])
        # if len(post_list) < config.LAST_POSTS_COMMAND_COUNT:
        #     self.bot.send_message(
        #         chat_id=chat_id,
        #         text=messages.NO_MORE_POSTS_TEXT
        #     )
    def answer_topic_info_query(self,
        query: CallbackQuery,
        chat_id: str,
        topic: topics.Topic,
        photo_url: str,
        is_subscribed: bool
    ):
        """Displays topic info (activated when clicked on a button)"""
        self.__answer_query(
            query=query,
            answer_text=None,
            edit_text=messages.SELECTED_TEXT + " " + topic.hashtag
        )
        self.__display_topic_info(
            chat_id=chat_id,
            topic=topic,
            photo_url=photo_url,
            is_subscribed=is_subscribed
        )
    def answer_subscribe_query(self, query: CallbackQuery, topic: topics.Topic):
        """Handles visual feedback when user subscribes to a topic through a button"""
        self.__answer_query(
            query=query,
            answer_text=messages.SUBSCRIBED_TEXT + " " + topic.hashtag,
            edit_text=topic.description + "\n" + messages.SUBSCRIBED_INLINE
        )
    def answer_unsubscribe_query(self, query: CallbackQuery, topic: topics.Topic):
        """Handles visual feedback when user unsubscribes from a topic through a button"""
        self.__answer_query(
            query=query,
            answer_text=messages.UNSUBSCRIBED_TEXT + " " + topic.hashtag,
            edit_text=topic.description + "\n" + messages.UNSUBSCRIBED_INLINE
       )

    def __answer_query(self, query: CallbackQuery, answer_text: Union[str, None], edit_text: str):
        query.answer(answer_text)
        try:
            query.edit_message_text(edit_text)
        except TelegramError:
            query.edit_message_caption(edit_text)

    def __display_topic_info(self, chat_id: str, topic: topics.Topic, photo_url, is_subscribed):
        if is_subscribed:
            button_text = messages.UNSUBSCRIBE_TEXT
            prefix = query_prefixes.TOPIC_UNSUBSCRIBE_PREFIX
        else:
            button_text = messages.SUBSCRIBE_TEXT
            prefix = query_prefixes.TOPIC_SUBSCRIBE_PREFIX
        buttons = [[
            InlineKeyboardButton(
                button_text,
                callback_data=query_prefixes.create_topic_query(topic, prefix)
            )
        ]]
        caption = f"""
        {topic.hashtag}
        {topic.description}
        """
        self.bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    def __internal_topic_list(
        self,
        chat_id: str,
        text: str,
        topic_to_button: Callable[[topics.Topic], InlineKeyboardButton]
    ):
        buttons = [
            [topic_to_button(topic)]
            for topic in topics.TOPICS_LIST
        ]
        self.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    def __display_post(self, post: Post, chat_id: str):
        text = post.topic.hashtag + '\n' + post.get_vk_link() + '\n' + post.text
        can_display_caption = len(text) < 1000 # when len > 1000 telegram can't display the caption,
        if post.photos:
            caption = text if can_display_caption else None
            self.bot.send_media_group(
                chat_id=chat_id,
                media=[InputMediaPhoto(media=post.photos[0], caption=caption)] +
                    [InputMediaPhoto(media=photo) for photo in post.photos[1:]]
            )
        # so you need to send it as a separate message
        if not post.photos or not can_display_caption:
            self.bot.send_message(
                chat_id=chat_id,
                text=text,
                disable_web_page_preview=True
            )
