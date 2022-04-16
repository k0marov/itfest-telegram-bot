"""Module that provides the TelegramInput class"""
from typing import Callable
from dataclasses import dataclass
from telegram import Bot as TelegramBot, CallbackQuery
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
)
import lib.telegram.query_prefixes as query_prefixes
import lib.core.topics as topics
import lib.core.messages as messages

@dataclass(frozen=True)
class TelegramInputCallbacks:
    """Callbacks for the TelegramInput class"""
    on_start: Callable[[str], None]
    on_topics: Callable[[str], None]
    on_contacts: Callable[[str], None]
    on_info: Callable[[str], None]
    on_choose_last_posts: Callable[[str], None]
    on_get_last_posts_query: Callable[[CallbackQuery, str, topics.Topic], None]
    on_topic_info_query: Callable[[CallbackQuery, str, topics.Topic], None]
    on_subscribe_query: Callable[[CallbackQuery, str, topics.Topic], None]
    on_unsubscribe_query: Callable[[CallbackQuery, str, topics.Topic], None]

class TelegramInput:
    """Class that handles input into the Telegram bot from the user
    by calling the provided callbacks"""
    def __init__(self, bot_instance: TelegramBot, callbacks: TelegramInputCallbacks):
        self.bot = bot_instance
        self.callbacks = callbacks

    def __start_handler(self, update, _):
        self.callbacks.on_start(update.effective_chat.id)
    def __text_message_handler(self, update, _):
        text = update.message.text
        chat_id = update.effective_chat.id
        if text == messages.TOPICS_COMMAND:
            self.callbacks.on_topics(chat_id)
        elif text == messages.INFO_COMMAND:
            self.callbacks.on_info(chat_id)
        elif text == messages.CONTACTS_COMMAND:
            self.callbacks.on_contacts(chat_id)
        elif text == messages.LAST_POSTS_COMMAND:
            self.callbacks.on_choose_last_posts(chat_id)
    def __callback_query_handler(self, update, _) -> None:
        query = update.callback_query
        topic = query_prefixes.get_topic_from_query(query.data)
        # instead of multiple if/elif branches, to reduce code duplication
        query_callbacks_with_prefixes = [
            (query_prefixes.TOPIC_INFO_PREFIX, self.callbacks.on_topic_info_query),
            (query_prefixes.TOPIC_SUBSCRIBE_PREFIX, self.callbacks.on_subscribe_query),
            (query_prefixes.TOPIC_UNSUBSCRIBE_PREFIX, self.callbacks.on_unsubscribe_query),
            (query_prefixes.TOPIC_LAST_POSTS_PREFIX, self.callbacks.on_get_last_posts_query),
        ]
        for prefix, callback in query_callbacks_with_prefixes:
            if query_prefixes.is_query_with_prefix(query.data, prefix):
                print(prefix)
                callback(
                    query=query,
                    chat_id=update.effective_chat.id,
                    topic=topic
                )

    def start_updater(self) -> None:
        """Starts the handling of user updates"""
        updater = Updater(token=self.bot.token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", self.__start_handler))
        dispatcher.add_handler(MessageHandler(Filters.text, self.__text_message_handler))
        dispatcher.add_handler(CallbackQueryHandler(self.__callback_query_handler))
        updater.start_polling()
