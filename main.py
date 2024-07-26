import threading
import time
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import Forbidden
import sqlite3
from stalcraft import AppClient, Region
from config import *
import asyncio

TOKEN = '7174657588:AAHW6lPSO0fOKyW59tAwc_EXMXWfmwUqYog'
client = AppClient(apptoken)
emission_started = False

# Функция для старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    chat_id = update.message.chat.id

    # Добавляем пользователя в базу данных
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, chat_id) VALUES (?, ?)', (user.id, chat_id))
    conn.commit()
    conn.close()

    await update.message.reply_text('Вы зарегистрированы для получения уведомлений о выбросах.')

# Асинхронная функция для отправки сообщений во все чаты
async def send_message_to_all_chats(application, message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT chat_id FROM users')
    chat_ids = cursor.fetchall()
    conn.close()

    for chat_id in chat_ids:
        try:
            await application.bot.send_message(chat_id=chat_id[0], text=message)
        except Forbidden:
            continue

# Функция для проверки выбросов
def check_emissions(application):
    global emission_started
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        result = client.emission(Region.RU)  # Предполагается, что client и Region определены
        if result.current_start is not None and not emission_started:
            loop.run_until_complete(send_message_to_all_chats(application, "Выброс начался"))
            emission_started = True
        elif result.current_start is None and emission_started:
            loop.run_until_complete(send_message_to_all_chats(application, "Выброс закончился"))
            emission_started = False
        time.sleep(5)

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    emission_thread = threading.Thread(target=check_emissions, args=(application,))
    emission_thread.start()

    application.run_polling()

if __name__ == '__main__':
    main()