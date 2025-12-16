import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Загружаем тексты
with open("data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

def start(update: Update, context: CallbackContext):
    keyboard = [["🌀 Интеллектуальная охота"], ["📊 Прогресс"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "🌀 Curly Meme: Context Hunt

"
        "Философия, культура, немного техники.
"
        "Жми «🌀 Интеллектуальная охота», чтобы начать.",
        reply_markup=reply_markup,
    )

def hunt(update: Update, context: CallbackContext):
    # Берём любой B1‑текст
    texts = DATA["B1"]["texts"]
    text = texts[0]["text"]
    update.message.reply_text(
        f"📖 Текст уровня B1:

{text}

"
        "Пока просто читаем. Позже добавим квиз 🙂"
    )

def text_handler(update: Update, context: CallbackContext):
    msg = update.message.text
    if "Интеллектуальная охота" in msg:
        return hunt(update, context)
    update.message.reply_text("Напиши /start или жми «🌀 Интеллектуальная охота».")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
