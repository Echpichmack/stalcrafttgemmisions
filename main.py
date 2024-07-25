import threading
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, ApplicationBuilder, ContextTypes
import sqlite3
from stalcraft import AppClient, Region
from config import *

TOKEN = '7174657588:AAHW6lPSO0fOKyW59tAwc_EXMXWfmwUqYog'
client = AppClient(apptoken)
emission_started = False

async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    chat_id = update.message.chat.id
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, chat_id) VALUES (?, ?)', (user.id, chat_id))
    conn.commit()
    conn.close()
    await update.message.reply_text('🤩 Теперь Вы получаете уведомления о выбросах 🤩')

def check_emissions(application: ApplicationBuilder):
    global emission_started
    while True:
        result = client.emission(Region.RU)
        if result.current_start is not None and not emission_started:
            send_message_to_all_chats(application, "🌩 Выброс начался 🌩")
            emission_started = True
        elif result.current_start is None and emission_started:
            send_message_to_all_chats(application, "⛅️ Выброс закончился ⛅️")
            emission_started = False
        time.sleep(5)

def send_message_to_all_chats(application: ApplicationBuilder, message: str):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT chat_id FROM users')
    chat_ids = cursor.fetchall()
    conn.close()
    bot = application.bot
    for chat_id in chat_ids:
        bot.send_message(chat_id=chat_id[0], text=message)

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    emission_thread = threading.Thread(target=check_emissions, args=(application,))
    emission_thread.start()

    application.run_polling()

if __name__ == '__main__':
    main()
