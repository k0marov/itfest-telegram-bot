"""Module containing the Bot class"""
import time
from lib.database.database import Database
from lib.telegram.telegram import Telegram, TelegramCallbacks
from lib.vk.vk import Vk
from lib.timer.timer import Timer
from lib.core import topics
import lib.core.config as config


class Bot:
    """Provides Database and Vk for TelegramBot and also starts a timer to send new posts"""
    def __init__(self, tg_token, vk_token):
        self.vk = Vk(vk_token)
        self.db = Database()
        telegram_callbacks = TelegramCallbacks(
            subscribe=self.db.add_user_to_topic,
            unsubscribe=self.db.del_user_from_topic,
            is_subscribed=self.db.is_subscribed,
            get_group_avatar=self.vk.get_group_avatar,
            get_last_posts=self.vk.get_last_n_posts
        )
        self.telegram = Telegram(tg_token, telegram_callbacks)
        self.timer = Timer(
            duration_minutes=config.POST_UPDATING_INTERVAL,
            callback=self.__periodic_callback
        )

    def start(self):
        """Starts the Telegram Bot and the Periodic Timer for sending new posts"""
        self.telegram.start_bot()
        self.timer.start()

    def __periodic_callback(self):
        for topic in topics.TOPICS_LIST:
            new_posts = self.vk.get_posts_for_last_n_minutes(
                topic,
                (config.TIME_TO_SLEEP_AFTER_REQUEST/60*len(topics.TOPICS_LIST)
                    +
                config.POST_UPDATING_INTERVAL)
            )
            users = self.db.get_users_with_topic(topic)
            self.telegram.display_posts_for_users(new_posts, list(users))
            time.sleep(config.TIME_TO_SLEEP_AFTER_REQUEST)
