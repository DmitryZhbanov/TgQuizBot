import aiosqlite
from aiogram import types, Dispatcher
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from quiz_data import quiz_data
from db import get_quiz_state, update_quiz_state

DB_NAME = None

def set_db_name(db_name: str):
    global DB_NAME
    DB_NAME = db_name

def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()
    for index, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(text=option, callback_data=f"answer|{index}"))
    builder.adjust(1)
    return builder.as_markup()

async def get_question(message: types.Message, user_id: int):
    question_index, _ = await get_quiz_state(user_id)
    question_data = quiz_data[question_index]
    kb = generate_options_keyboard(question_data['options'])
    await message.answer(question_data['question'], reply_markup=kb)

async def new_quiz(message: types.Message):
    user_id = message.from_user.id
    await update_quiz_state(user_id, 0, 0)
    await get_question(message, user_id)

def register_handlers(dp: Dispatcher):

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="Начать игру"))
        await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

    @dp.message(lambda message: message.text in ["Начать игру", "/quiz"])
    async def cmd_quiz(message: types.Message):
        await message.answer("Давайте начнем квиз!")
        await new_quiz(message)

    @dp.callback_query(lambda callback: callback.data and callback.data.startswith("answer|"))
    async def answer_handler(callback: types.CallbackQuery):
        parts = callback.data.split("|")
        if len(parts) < 2:
            return
        try:
            user_answer_index = int(parts[1])
        except ValueError:
            return

        current_question_index, current_score = await get_quiz_state(callback.from_user.id)
        question_data = quiz_data[current_question_index]
        user_answer = question_data['options'][user_answer_index]

        await callback.bot.edit_message_reply_markup(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )

        await callback.message.answer(f"Ваш ответ: {user_answer}")

        if user_answer_index == question_data['correct_option']:
            await callback.message.answer("Верно!")
            current_score += 1
        else:
            correct_answer = question_data['options'][question_data['correct_option']]
            await callback.message.answer(f"Неправильно. Правильный ответ: {correct_answer}")

        current_question_index += 1
        await update_quiz_state(callback.from_user.id, current_question_index, current_score)

        if current_question_index < len(quiz_data):
            await get_question(callback.message, callback.from_user.id)
        else:
            await callback.message.answer(f"Это был последний вопрос. Квиз завершен!\nВаш результат: {current_score} из {len(quiz_data)}.")

    @dp.message(Command("stats"))
    async def cmd_stats(message: types.Message):
        async with aiosqlite.connect(DB_NAME) as db:
            async with db.execute('SELECT user_id, score FROM quiz_state') as cursor:
                rows = await cursor.fetchall()
        if rows:
            stats_text = "Статистика игроков:\n"
            for row in rows:
                stats_text += f"Пользователь {row[0]}: {row[1]} баллов\n"
        else:
            stats_text = "Статистика отсутствует."
        await message.answer(stats_text)
