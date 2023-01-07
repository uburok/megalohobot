from datetime import datetime, timedelta
from os import getenv

from dotenv import load_dotenv
from requests import get
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Updater, CommandHandler, JobQueue

import settings
from db import MegalohobotDB
from structures import Chat, Event

# All confidential info is stored as environment vars
load_dotenv(".env")
API_TOKEN = getenv("MLB_TELEGRAM_TOKEN")
BOT_OWNER_ID = int(getenv("MLB_TELEGRAM_BOT_OWNER"))


def _get_text_from_say_command(update: Update, command):
    command_len = len(command)
    text = update.message.text[command_len:]
    entities = []
    for i in update.message.entities:
        if i.type != "bot_command":
            i.offset -= command_len
            entities.append(i)
    return text, entities


def _is_valid_date(date_text):
    if len(date_text) != 5:
        return False
    try:
        datetime.strptime(date_text, "%d.%m")
    except ValueError:
        return False
    return True


# Bot Handlers
def help_handler(update: Update, _: CallbackContext):
    if not update.effective_chat:  # Bypass non-chat updates (inline queries, polls etc)
        return
    message = """Привет! Меня зовут megalohobot и на данный момент я поддерживаю следующие команды:
  Общее:
    /help, /info - вывод этой справки.
    /start - инициализация чата (для работы с событиями и т.п.).
    /stop - прекратить работу в чате (все данные сохранятся). Возобновить работу можно командой /start.
    /ip - сказать свой айпишник (только владельцу бота в привате).
    /say <текст> - сказать <текст>. Твое сообщение с этой командой удалится (боту нужны права админа в чате).
  Работа с событиями:
    /events - посмотреть все события чата
    /add_event <date> <title> - добавить событие, формат даты дд.мм (напр., "/add_event 01.01 Новый год!!!")
    /del_event <date> <title> - удалить событие"""
    update.effective_chat.send_message(message)


def start_handler(update: Update, _: CallbackContext):
    if not update.effective_chat:  # Bypass non-chat updates (inline queries, polls etc)
        return
    db = MegalohobotDB(settings.DB_PATH)
    chat = Chat(update.effective_chat.id)
    status = db.add_chat(chat)
    if status:
        update.effective_chat.send_message("Готово. Теперь можно пользоваться всеми моими функциями.")
    else:
        update.effective_chat.send_message("Что-то пошло не так, позовите айтишника.")


def stop_handler(update: Update, _: CallbackContext):
    if not update.effective_chat:  # Bypass non-chat updates (inline queries, polls etc)
        return
    db = MegalohobotDB(settings.DB_PATH)
    chat = Chat(update.effective_chat.id)
    status = db.disable_chat(chat)
    if status:
        update.effective_chat.send_message("Замолкаю. Чтоб продолжить мою работу здесь, запустите меня заново командой /start.")
    else:
        update.effective_chat.send_message("Что-то пошло не так, позовите айтишника.")


def ip_handler(update: Update, _: CallbackContext):
    if not update.effective_chat:  # Bypass non-chat updates (inline queries, polls etc)
        return
    db = MegalohobotDB(settings.DB_PATH)
    chat = Chat(update.effective_chat.id)
    if not db.check_chat_status(chat):
        update.effective_message.reply_text("Меня выключили или забыли запустить в этом чате. Скомандуйте /start, чтобы я смог начать работу.")
        return
    if chat.chat_id == BOT_OWNER_ID:
        host_ip = get('https://api.ipify.org').text
        update.effective_message.reply_text(host_ip)
    else:
        update.effective_message.reply_text("Это конфиденциальная инфа, я могу её озвучить только в привате с хозяином.")


def say_handler(update: Update, _: CallbackContext):
    if not update.effective_chat:  # Bypass non-chat updates (inline queries, polls etc)
        return
    db = MegalohobotDB(settings.DB_PATH)
    chat = Chat(update.effective_chat.id)
    if not db.check_chat_status(chat):
        update.effective_message.reply_text("Меня выключили или забыли запустить в этом чате. Скомандуйте /start, чтобы я смог начать работу.")
        return
    if update.effective_chat.type in ("group", "supergroup", "channel"):
        text, entities = _get_text_from_say_command(update, "/say ")
        update.effective_message.delete()
        update.effective_chat.send_message(text=text, entities=entities)
    else:
        update.effective_chat.send_message("Я не поддерживаю эту команду в приватных чатах :(")


def events_handler(update: Update, _: CallbackContext):
    if not update.effective_chat:  # Bypass non-chat updates (inline queries, polls etc)
        return
    db = MegalohobotDB(settings.DB_PATH)
    chat = Chat(update.effective_chat.id)
    if not db.check_chat_status(chat):
        update.effective_message.reply_text("Меня выключили или забыли запустить в этом чате. Скомандуйте /start, чтобы я смог начать работу.")
        return
    events = db.get_chat_events(chat)
    if not events:
        msg = "В этом чате пока нет событий."
    else:
        msg = "Список событий чата:\n"
        for i in events:
            msg += f"{i.date} {i.title}\n"
    update.effective_chat.send_message(msg)


def add_event_handler(update: Update, context: CallbackContext):
    if not update.effective_chat:  # Bypass non-chat updates (inline queries, polls etc)
        return
    db = MegalohobotDB(settings.DB_PATH)
    chat = Chat(update.effective_chat.id)
    if not db.check_chat_status(chat):
        update.effective_message.reply_text("Меня выключили или забыли запустить в этом чате. Скомандуйте /start, чтобы я смог начать работу.")
        return
    # Check if event string is legit: date format and title presence
    try:
        date = context.args[0]
        if not _is_valid_date(date):
            raise ValueError
        if not context.args[1]:
            raise ValueError
        title = ' '.join(i for i in context.args[1:])
        title_sql_ready = title.replace("'", "''")  # escaping ' symbol in sql query
    except (IndexError, ValueError):
        update.effective_message.reply_text("Что-то я не пойму тебя. События надо добавлять в формате: дд.мм описание события")
        return
    event = Event(chat.chat_id, title, date)
    event_sql_ready = Event(chat.chat_id, title_sql_ready, date)
    existing_events = db.get_chat_events(chat)
    if event in existing_events:
        update.effective_message.reply_text("Такое событие у меня уже записано. Обязательно напомню, не переживай.")
        return
    status = db.add_event(event_sql_ready)
    if status:
        update.effective_chat.send_message(f"Добавил событие: {date} - {title}")
    else:
        update.effective_chat.send_message("Что-то пошло не так, позовите айтишника.")


def del_event_handler(update: Update, context: CallbackContext):
    if not update.effective_chat:  # Bypass non-chat updates (inline queries, polls etc)
        return
    db = MegalohobotDB(settings.DB_PATH)
    chat = Chat(update.effective_chat.id)
    if not db.check_chat_status(chat):
        update.effective_message.reply_text("Меня выключили или забыли запустить в этом чате. Скомандуйте /start, чтобы я смог начать работу.")
        return
    # Check if event string is legit: date format and title presence
    try:
        date = context.args[0]
        if not _is_valid_date(date):
            raise ValueError
        if not context.args[1]:
            raise ValueError
        title = ' '.join(i for i in context.args[1:])
        title_sql_ready = title.replace("'", "''")  # escaping ' symbol in sql query
    except (IndexError, ValueError):
        update.effective_message.reply_text("Что-то я не пойму тебя. События надо добавлять в формате: дд.мм описание события")
        return
    event = Event(chat.chat_id, title, date)
    event_sql_ready = Event(chat.chat_id, title_sql_ready, date)
    existing_events = db.get_chat_events(chat)
    if event in existing_events:
        status = db.delete_event(event_sql_ready)
        if status:
            update.effective_chat.send_message(f"Удалил событие: {date} - {title}.")
        else:
            update.effective_chat.send_message("Что-то пошло не так, позовите айтишника.")
    else:
        update.effective_chat.send_message("Не нашел такого события у себя, удалять нечего.")


def remind_events_worker(context: CallbackContext):
    db = MegalohobotDB(settings.DB_PATH)
    events = db.get_all_events()
    now = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(hours=settings.DEFAULT_REMIND_TZ)
    now_events = []
    for i in events:
        event_time = datetime.strptime(f"{i.date} {i.time}", "%d.%m %H:%M").replace(year=now.year)
        if event_time == now:
            now_events.append(i)
    if now_events:
        chats = set((i.chat_id for i in now_events))
        for chat in chats:
            if not db.check_chat_status(Chat(chat)):
                continue
            greeting = f"Вспомним, что сегодня у нас особенный день. Вот что у меня записано:\n"
            for event in now_events:
                if event.chat_id == chat:
                    greeting += event.title + "\n"
            greeting += "*Поздравим же всех причастных!!!*"
            context.dispatcher.bot.send_message(chat, greeting, parse_mode="Markdown")


def main():
    # Initializing bot
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    # Adding command handlers
    dispatcher.add_handler(CommandHandler("help", help_handler))
    dispatcher.add_handler(CommandHandler("info", help_handler))
    dispatcher.add_handler(CommandHandler("start", start_handler))
    dispatcher.add_handler(CommandHandler("stop", stop_handler))
    dispatcher.add_handler(CommandHandler("ip", ip_handler))
    dispatcher.add_handler(CommandHandler("say", say_handler))
    dispatcher.add_handler(CommandHandler("events", events_handler))
    dispatcher.add_handler(CommandHandler("add_event", add_event_handler))
    dispatcher.add_handler(CommandHandler("del_event", del_event_handler))

    # Adding event jobs
    events_job_queue = JobQueue()
    events_job_queue.set_dispatcher(dispatcher)
    events_job_queue.run_repeating(remind_events_worker, 60)
    events_job_queue.start()

    # Starting bot
    updater.start_polling(drop_pending_updates=True)
    updater.idle()


if __name__ == "__main__":
    main()
