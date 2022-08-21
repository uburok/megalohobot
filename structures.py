from dataclasses import dataclass

import settings


@dataclass
class Chat:
    chat_id: int


@dataclass
class Event:
    chat_id: int
    title: str
    date: str = settings.DEFAULT_REMIND_DATE
    time: str = settings.DEFAULT_REMIND_TIME
