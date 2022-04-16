"""Module that provides the Database class"""
import sqlite3
from typing import Iterable, Iterator
from lib.core import topics


class Database:
    """Simple sqlite database"""

    class CursorIterator(Iterable):
        """Iterator that allows to use the cursor without loading everything into memory"""
        def __init__(self, cursor: sqlite3.Cursor, only_first_field: bool):
            self.cursor = cursor
            self.only_first_field = only_first_field
        def __iter__(self):
            return self
        def __next__(self):
            row = self.cursor.fetchone()
            if not row:
                raise StopIteration
            return row[0] if self.only_first_field else row

    db_path = "./lib/database/topics.db"


    def __init__(self):
        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self.db.execute("CREATE TABLE if not exists topics (topic_id text, user_id text)")
        self.db.commit()
    def __del__(self):
        self.db.close()
    def add_user_to_topic(self, user_id: str, topic: topics.Topic) -> None:
        """Subscribes the given user to the given topic"""
        self.db.execute("insert into topics(topic_id, user_id) VALUES(?, ?)", (topic.id, user_id,))
        self.db.commit()
    def del_user_from_topic(self, user_id: str, topic: topics.Topic) -> None:
        """Unsubscribes the given user from the given topic"""
        self.db.execute("delete from topics where topic_id = ? AND user_id = ?", (topic.id,user_id))
        self.db.commit()
    def get_users_with_topic(self, topic: topics.Topic) -> Iterator:
        """Returns all users that are subscribed to the given topic as an Iterator"""
        cursor = self.db.execute("select user_id from topics where topic_id = ?", (topic.id))
        return Database.CursorIterator(cursor, only_first_field=True)
    def is_subscribed(self, user_id: str, topic: topics.Topic) -> bool:
        """Returns true if the given user is subscribed to the given topic and false otherwise"""
        return self.db.execute(
            "select user_id from topics where topic_id = ? AND user_Id = ?",
            (topic.id, user_id)
        ).fetchone() is not None
