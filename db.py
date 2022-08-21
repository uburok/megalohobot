import sqlite3

from structures import Chat, Event


class MegalohobotDB:
    def __init__(self, db_path):
        self._connection = sqlite3.connect(db_path)
        self._cursor = self._connection.cursor()

        create_chat_table_query = """CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_chat_id INTEGER UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 1
            );"""
        create_events_table_query = f"""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id REFERENCES chats(id),
            title TEXT,
            date TEXT,
            time TEXT
            );"""
        self._cursor.execute(create_chat_table_query)
        self._cursor.execute(create_events_table_query)
        self._connection.commit()

    def __del__(self):
        self._connection.close()

    def add_chat(self, chat: Chat) -> bool:
        add_chat_query = f"""INSERT OR IGNORE INTO chats(telegram_chat_id) VALUES ({chat.chat_id});"""
        enable_chat_query = f"""UPDATE chats SET is_active = 1 WHERE telegram_chat_id = {chat.chat_id};"""
        try:
            self._cursor.execute(add_chat_query)
            self._cursor.execute(enable_chat_query)
            self._connection.commit()
        except Exception:
            return False
        return True

    def enable_chat(self, chat: Chat) -> bool:
        enable_chat_query = f"""UPDATE chats SET is_active = 1 WHERE telegram_chat_id = {chat.chat_id};"""
        try:
            self._cursor.execute(enable_chat_query)
            self._connection.commit()
        except Exception:
            return False
        return True

    def disable_chat(self, chat: Chat) -> bool:
        disable_chat_query = f"""UPDATE chats SET is_active = 0 WHERE telegram_chat_id = {chat.chat_id};"""
        try:
            self._cursor.execute(disable_chat_query)
            self._connection.commit()
        except Exception:
            return False
        return True

    def check_chat_status(self, chat: Chat) -> bool:
        check_chat_status_query = f"""SELECT is_active FROM chats WHERE telegram_chat_id = {chat.chat_id};"""
        try:
            self._cursor.execute(check_chat_status_query)
            status = self._cursor.fetchone()[0]
        except Exception:
            return None
        return bool(status)

    def add_event(self, event: Event) -> bool:
        chat_id_query = f"""SELECT id FROM chats WHERE telegram_chat_id = {event.chat_id};"""
        try:
            self._cursor.execute(chat_id_query)
            chat_id = self._cursor.fetchone()[0]
        except Exception:
            return False

        add_event_query = f"""INSERT INTO events(chat_id, title, date, time) VALUES 
            ({chat_id}, '{event.title}', '{event.date}', '{event.time}');"""
        try:
            self._cursor.execute(add_event_query)
            self._connection.commit()
        except Exception:
            return False
        return True

    def delete_event(self, event: Event) -> bool:
        delete_event_query = f"""DELETE FROM events WHERE
            chat_id IN (SELECT id FROM chats WHERE telegram_chat_id = {event.chat_id}) AND
            title = '{event.title}'AND
            date = '{event.date}' AND
            time = '{event.time}'
            ;"""
        try:
            self._cursor.execute(delete_event_query)
            self._connection.commit()
        except Exception:
            return False
        return True

    def get_chat_events(self, chat: Chat) -> [list, None]:
        get_events_query = f"""SELECT title, date, time FROM events
            JOIN chats ON chats.id = events.chat_id
            WHERE chats.telegram_chat_id = {chat.chat_id};"""
        try:
            self._cursor.execute(get_events_query)
            events = self._cursor.fetchall()
        except Exception:
            return None
        events = [Event(chat.chat_id, i[0], i[1], i[2]) for i in events]
        return events

    def get_all_events(self) -> [list, None]:
        get_events_query = f"""SELECT chats.telegram_chat_id, title, date, time FROM events
            JOIN chats ON chats.id = events.chat_id;"""
        try:
            self._cursor.execute(get_events_query)
            events = self._cursor.fetchall()
        except Exception:
            return None
        events = [Event(i[0], i[1], i[2], i[3]) for i in events]
        return events
