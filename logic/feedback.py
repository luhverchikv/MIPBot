# logic/feedback.py
from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db_manager.db import Database
from config import config
from menu.keyboard import start_keyboard
import asyncio


class FeedbackState(StatesGroup):
    waiting_for_feedback = State()


db = Database()
feedback_router = Router()


# Обработчик нажатия кнопки "оставить отзыв"
@feedback_router.callback_query(F.data == 'set_feedback')
async def process_feedback_callback(call: CallbackQuery, state: FSMContext):
    # Отправляем сообщение с просьбой оставить отзыв
    msg = await call.message.answer("Пожалуйста, напишите ваш отзыв.")

    # Сохраняем ID этого сообщения в FSM
    await state.update_data(feedback_msg_id=msg.message_id)

    # Устанавливаем состояние ожидания текста
    await state.set_state(FeedbackState.waiting_for_feedback)


# Обработчик текста от пользователя
@feedback_router.message(FeedbackState.waiting_for_feedback)
async def process_feedback(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    feedback_msg_id = data.get("feedback_msg_id")

    # Удаляем сообщение с просьбой написать отзыв (если оно существует)
    if feedback_msg_id:
        try:
            await bot.delete_message(message.chat.id, feedback_msg_id)
        except Exception:
            pass  # на случай, если сообщение уже удалено или не найдено

    feedback_text = message.text

    # Сохраняем отзыв в базе
    db.add_feedback(user_id=message.from_user.id, description=feedback_text, status=0)

    # Отправляем администраторам
    for admin_id in config.bot.admin_ids:
        await bot.send_message(admin_id, f"Получен новый отзыв:\n{feedback_text}")
    
    # Отвечаем пользователю
    ans_1 = await message.answer(
        "Спасибо за ваше предложение! Оно будет учтено, и мы обязательно рассмотрим его. Ваш вклад очень важен для нас!"
    )
    
    ans_2 = await message.answer(
        "Если у вас есть еще что-то, чем вы хотели бы поделиться, не стесняйтесь писать!📩"
    )
    await asyncio.sleep(30)
    await ans_1.delete()
    await ans_2.delete()
    await message.delete()

    # Завершаем состояние
    await state.clear()