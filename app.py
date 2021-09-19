import os

from dotenv import load_dotenv
from requests import get
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters

# All confidential info is stored as environment vars
load_dotenv(".env")
API_TOKEN = os.getenv("MLB_TELEGRAM_TOKEN")
BOT_OWNER_ID = int(os.getenv("MLB_TELEGRAM_BOT_OWNER"))

DB_NAME = "db.sqlite3"


def _get_text_from_say_command(update: Update, command):
    command_len = len(command)
    text = update.message.text[command_len:]
    entities = []
    for i in update.message.entities:
        if i.type != "bot_command":
            i.offset -= command_len
            entities.append(i)
    return text, entities


def get_host_ip(update: Update, _: CallbackContext):
    if update.message.chat.id == BOT_OWNER_ID:
        host_ip = get('https://api.ipify.org').text
        update.message.reply_text(host_ip)
    else:
        update.message.reply_text("Я тебя не понимаю:(")


def say_handler(update: Update, _: CallbackContext) -> None:
    """For groups only. Deletes command message and repeats message in his own name"""
    if update.message.chat.type in ("group", "supergroup", "channel"):
        text, entities = _get_text_from_say_command(update, "/say ")
        update.message.delete()
        update.effective_chat.send_message(text=text, entities=entities)
    else:
        update.message.reply_text("Я не поддерживаю эту команду в приватных чатах :(")


def main():
    # Initializing bot
    updater = Updater(API_TOKEN)
    dispatcher = updater.dispatcher

    # Adding command handlers
    dispatcher.add_handler(CommandHandler("ip", get_host_ip))
    dispatcher.add_handler(CommandHandler("say", say_handler))

    # Starting bot
    updater.start_polling(drop_pending_updates=True)
    updater.idle()


if __name__ == "__main__":
    main()
