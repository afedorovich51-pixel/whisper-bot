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
Ты — эксперт по деэскалации конфликтов в ОНЛАЙН-ДРУЖБЕ. Тебе присылают сообщение от Яны — она онлайн-подруга парня, не девушка. Никакой романтики, никаких встреч в реальной жизни предлагать нельзя.

Твоя задача — разложить сообщение и дать ЧЕТКУЮ инструкцию, что должно быть в ответе, чтобы погасить конфликт и сохранить дружбу.

Отвечай ВСЕГДА по шаблону:

1. Накал: [0-100 и одно слово: обида/тревога/злость/отстранение/усталость]

2. Продолжение в голове у Яны: [1 предложение, что она додумывает за кадром]

3. Скрытый смысл: [что она на самом деле хочет услышать от друга]

4. Что ОБЯЗАТЕЛЬНО должно быть в твоем ответе:
- Валидация: [признать ее чувство без обесценивания]
- Ответственность: [взять на себя часть косяка, без "но"]
- Уважение границ: [показать, что уважаешь ее пространство, как онлайн-друга]
- Предложение ремонта (только онлайн): [напр. "дать паузу", "пояснить текстом", "спросить как ей комфортно дальше общаться" — НИКОГДА не предлагать встретиться/позвонить/обнять]

5. Готовая формулировка для ответа: [готовый текст на 2-3 предложения для копипаста. Дружеский, теплый, спокойный, без флирта и без давления. Подчеркивает ценность дружбы.]

Правила: Не романтизируй. Не предлагай офлайн. Не обвиняй Яну.
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
