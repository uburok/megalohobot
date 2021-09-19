import sqlite3
from dataclasses import dataclass


@dataclass
class Chat:
    chat_id: int
    chat_type: str
    chat_desc: str = ""

@dataclass
class User:
    user_id: int
    first_name: str
    username: str = ""
    last_name: str = ""
    birthday: str = ""
    desc: str = ""


CREATE_TABLE_CHATS_QUERY = """
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER UNIQUE NOT NULL,
        type TEXT NOT NULL,
        desc TEXT DEFAULT '')
    """

CREATE_TABLE_USERS_QUERY = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        username TEXT DEFAULT '',
        last_name TEXT DEFAULT '',
        birthday TEXT DEFAULT '',
        desc TEXT DEFAULT '')
    """

CREATE_TABLE_USERS_IN_CHATS_QUERY = """
    CREATE TABLE users_in_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id),
        chat_id INTEGER NOT NULL REFERENCES chats(id),
        congrats_in_chat INTEGER)    
    """


conn = sqlite3.connect("megalohobot.db")
cur = conn.cursor()


def db_create_chat(chat: Chat):
    pass


def db_create_user(user: User):
    pass


