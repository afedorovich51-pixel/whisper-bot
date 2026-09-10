import os
import threading
from flask import Flask
import telebot
from openai import OpenAI

# --- 1. ДОМИК ДЛЯ РЕНДЕРА (чтобы Рендер видел что мы живые) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "whisper-bot is live! Our translator работает!"

# --- 2. НАСТРОЙКИ РОБОТА ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

PROMPT = """
Ты - бот шепота. Тебе присылают сообщение от партнера.
Твоя задача - разобрать его.
Верни ответ СТРОГО в формате:
Накал: [число от 0 до 100]/100. Если >70 - сделай паузу, не отвечай сразу.
Продолжение в голове: [что человек на самом деле думает, 1 фраза]
Скрытый смысл: [что он хочет на самом деле]
Формулировка для ответа: [мягкий, теплый ответ от имени пользователя, 1-2 предложения]

Будь кратким, теплым, по-русски.
"""

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот шепота готов. Перешли мне сообщение из чата с партнером.")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    try:
        # Берем текст, даже если это пересланное сообщение
        text = message.text or message.caption or ""
        if not text:
            return

        # Если нет ключа OpenAI - сразу говорим
        if not client:
            bot.reply_to(message, "Ошибка: нет OPENAI_API_KEY в Render -> Environment. Добавь его!")
            return

        # Запрос к нейросети
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )
        answer = response.choices[0].message.content
        bot.reply_to(message, answer)

    except Exception as e:
        # ВАЖНО: теперь он не будет молчать, а напишет ошибку и в лог
        print(f"ОШИБКА БОТА: {e}")
        try:
            bot.reply_to(message, f"Я упал, но я тут. Ошибка: {e}")
        except:
            pass

# --- 3. ЗАПУСКАЕМ ВСЕ ВМЕСТЕ ---
def run_bot():
    print("Робот завелся! Our translator слушает Телеграм...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Робота запускаем в соседней комнате (поток)
    threading.Thread(target=run_bot, daemon=True).start()
    # А домик запускаем тут
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
