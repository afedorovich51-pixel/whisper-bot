import os
import threading
from flask import Flask
import telebot
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

SYSTEM_PROMPT = """
Ты — эксперт по деэскалации конфликтов в паре. Тебе присылают сообщение от девушки Яны.
Твоя задача — разложить сообщение и дать парню ЧЕТКУЮ инструкцию, что должно быть в его ответе, чтобы погасить конфликт.

Отвечай ВСЕГДА по этому шаблону, коротко и по делу:

1. Накал: [оценка 0-100 и одно слово: обида/тревога/злость/отстранение]

2. Продолжение в голове у Яны: [1 предложение, что она додумывает за кадром]

3. Скрытый смысл: [что она на самом деле хочет услышать]

4. Что ОБЯЗАТЕЛЬНО должно быть в твоем ответе (чтобы погасить):
- Валидация: [фраза, которой признать ее чувство, напр. "Понимаю, тебе обидно, что..."]
- Ответственность: [фраза, где взять на себя часть вины без оправданий]
- Привязанность: [фраза, где показать, что она важна]
- Предложение ремонта: [конкретное действие, что сделать дальше]

5. Готовая формулировка для ответа: [напиши готовый текст на 2-3 предложения, который можно скопировать Яне. Спокойный, теплый, без оправданий.]

Правила: Не обвиняй Яну. Не пиши общие советы. Пиши конкретные фразы.
"""

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Привет! Я — твой шепот. Перешли мне любое сообщение от Яны, и я скажу, что в нем на самом деле и что ответить, чтобы погасить конфликт.")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle(m):
    try:
        if m.text.startswith('/'):
            return
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": m.text}
            ],
            temperature=0.7
        )
        bot.reply_to(m, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(m, f"Я упал, но я тут. Ошибка: {e}")

def run_bot():
    bot.infinity_polling()

threading.Thread(target=run_bot, daemon=True).start()

@app.route('/')
def home():
    return "Bot is Live"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
