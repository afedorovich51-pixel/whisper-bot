import os
import threading
import time
import telebot
from flask import Flask
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

SYSTEM_PROMPT = "Ты - шептун. Ты анализируешь сообщение девушки Яны и говоришь парню что у нее в голове. Формат: Накал: X/100, Продолжение в голове:..., Что делать:..."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я шептун. Перешли мне сообщение от Яны.")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    try:
        if not message.text:
            return
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Я упал, но я тут. Ошибка: {e}")

def run_bot():
    print("Удаляю двойников...")
    bot.remove_webhook()
    time.sleep(2)
    print("Запускаюсь один!")
    bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=30)

@app.route('/')
def home():
    return "Bot is alive"

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
