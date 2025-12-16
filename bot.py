import os
import logging
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from game import CurlyMemeGame

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
game = CurlyMemeGame()

class GameStates(StatesGroup):
    playing = State()
    quiz = State()

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌀 Интеллектуальная охота")],
            [KeyboardButton(text="📚 Темы"), KeyboardButton(text="📊 Прогресс")],
            [KeyboardButton(text="💭 Цитата дня")]
        ],
        resize_keyboard=True
    )

@dp.message(Command('start'))
async def start(msg: types.Message):
    await msg.answer(
        "🌀 **Curly Meme: Context Hunt**

"
        "Для мыслящих людей:
"
        "• Философия (Сократ → Деррида)
"
        "• Культура & искусство
"
        "• Бизнес-идеи

"
        "Найди слова → раскрой смысл → создай свои ценности ✨",
        reply_markup=main_keyboard(), parse_mode='Markdown'
    )

@dp.message(F.text == "🌀 Интеллектуальная охота")
async def start_hunt(msg: types.Message, state: FSMContext):
    level = 'B1'  # Default для интеллектуалов
    text_data = game.get_text(level)
    
    await state.update_data(level=level, text=text_data['text'], quiz=text_data['words'])
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Готово! Показать слова", callback_data="show_words")]
    ])
    
    await msg.answer(
        f"📖 **Текст уровня {level}:**

{text_data['text']}

"
        "🔍 Найди слова **в контексте** и жми кнопку!",
        reply_markup=markup, parse_mode='Markdown'
    )
    await state.set_state(GameStates.playing)

@dp.callback_query(F.data == "show_words", GameStates.playing)
async def show_words(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    words = [w['word'] for w in data['quiz']]
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=word, callback_data=f"quiz_{i}")] 
        for i, word in enumerate(words)
    ])
    
    await callback.message.edit_text(
        f"🎯 **Найденные слова:**
{', '.join(words)}

"
        "Выбери слово для квиза:",
        reply_markup=markup, parse_mode='Markdown'
    )

@dp.callback_query(F.data.startswith("quiz_"), GameStates.playing)
async def quiz_word(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split('_')[1])
    data = await state.get_data()
    quiz = data['quiz'][idx]
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=quiz['quiz'][0], callback_data=f"answer_0_{idx}"),
            InlineKeyboardButton(text=quiz['quiz'][1], callback_data=f"answer_1_{idx}")
        ],
        [InlineKeyboardButton(text=quiz['quiz'][2], callback_data=f"answer_2_{idx}")]
    ])
    
    await callback.message.edit_text(
        f"❓ **Что значит '{quiz['word']}'?**

"
        f"✅ Правильный перевод: *{quiz['ru']}*",
        reply_markup=markup, parse_mode='Markdown'
    )

@dp.callback_query(F.data.startswith("answer_"), GameStates.quiz)
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split('_')
    answer_idx = int(parts[1])
    word_idx = int(parts[2])
    
    data = await state.get_data()
    quiz = data['quiz'][word_idx]
    correct = 0
    
    points = 100 if answer_idx == correct else 0
    game.update_score(callback.from_user.id, points)
    
    result = "✅ Верно!" if answer_idx == correct else "❌ Неправильно"
    await callback.message.edit_text(
        f"{result}

"
        f"**{quiz['word']}** = *{quiz['ru']}*
"
        f"+{points} очков

"
        "Готов к следующему раунду?",
        reply_markup=main_keyboard(), parse_mode='Markdown'
    )
    await state.clear()

@dp.message(F.text == "📊 Прогресс")
async def stats(msg: types.Message):
    score = game.get_score(msg.from_user.id)
    await msg.answer(f"📈 Твой счёт: **{score}** очков
Продолжай охоту за смыслом! ✨", parse_mode='Markdown')

@dp.message(F.text == "💭 Цитата дня")
async def quote(msg: types.Message):
    quotes = [
        "«Я знаю, что ничего не знаю» — Сократ",
        "«Стань тем, кто ты есть» — Ницше",
        "«Смыслы не существуют, мы их создаём» — Деррида"
    ]
    await msg.answer(f"💭 *{random.choice(quotes)}*", parse_mode='Markdown')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
