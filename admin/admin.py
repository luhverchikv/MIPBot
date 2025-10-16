# admin/specialist.py

from aiogram import Router, F, Bot
from aiogram.types import Message, Contact, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
import tempfile
import os
#from admin.keyboard import 
from aiogram.filters import Command
import asyncio
from admin.broadcast import send_broadcast_message
from db_manager.db import Database
from config import config
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.input_file import BufferedInputFile

from admin.report import generate_report


db = Database()

class SpecialistStates(StatesGroup):
    waiting_for_broadcast_content = State()
    waiting_for_answer_specialist = State()


admin_router = Router()


# --- ВЫБОР ДЕЙСТВИЯ ---
@admin_router.message(Command("admin"))
async def start_admin(message: Message):
    
    # Проверяем, что юзер в списке админов
    if not db.is_admin(message.from_user.id):
        await message.answer("🚫 У вас нет прав для доступа к админ-панели.")
        return

    # Получаем количество незакрытых отзывов
    count = db.count_feedback_with_status_zero()

    # Формируем текст сообщения
    text = f"У вас {count} незакрытых задач, выберите действие:"

    # Формируем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 Незакрытые задачи", callback_data="show_open_feedbacks")],
        [InlineKeyboardButton(text="🗂️ Все задачи", callback_data="show_all_feedbacks")],
        [InlineKeyboardButton(text="📝 Сделать рассылку", callback_data="start_broadcast")],
        [InlineKeyboardButton(text="📊 Отчет", callback_data="generate_report")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_callback")]
    ])
    
    await message.answer(text, reply_markup=keyboard)


# --- ЛОГИКА ОБРАБОТКИ НЕЗАКРЫТЫХ ОТЗЫВОВ ---
@admin_router.callback_query(F.data == "show_open_feedbacks")
async def show_open_feedbacks(call: CallbackQuery):
    #user_id = call.from_user.id
    if not db.is_admin(call.from_user.id):
        await message.answer("🚫 У вас нет прав для доступа к админ-панели.")
        return

    feedbacks = db.get_open_feedbacks()

    if not feedbacks:
        await call.message.edit_text("Незакрытых задач не найдено.")
        await call.answer()
        return

    for fid, f_user_id, description in feedbacks:
        description = description or ""
        text = f"Отзыв №{fid}\nСтатус: незакрыто\nТекст: {description}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="☑️ Изменить статус", callback_data=f"change_status:{fid}")],
            [InlineKeyboardButton(text="🔘 Ответить и Закрыть", callback_data=f"reply_close:{fid}")],
            [InlineKeyboardButton(text="🗑️ Удалить задачу", callback_data=f"delete_feedback:{fid}")],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_callback")]
        ])
        await call.message.answer(text, reply_markup=keyboard)
        await asyncio.sleep(0.5)

    await call.answer()


@admin_router.message(SpecialistStates.waiting_for_answer_specialist)
async def process_feedback_reply(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_user_id = data.get("reply_target_user_id")
    fid = data.get("reply_feedback_id")

    if not target_user_id or not fid:
        await message.answer("Ошибка: не удалось получить данные для ответа.")
        await state.clear()
        return

    reply_text = message.text or message.caption or ""
    if not reply_text:
        await message.answer("Пустой ответ. Пожалуйста, отправьте текст.")
        return

    # Отправляем сообщение пользователю
    try:
        await bot.send_message(chat_id=target_user_id, text=reply_text)
    except Exception as e:
        await message.answer(f"Не удалось отправить сообщение пользователю: {e}")
        # всё равно пометим как закрыто или можно не менять — в данном примере меняем статус только при успешной отправке
        await state.clear()
        return

    # Помечаем отзыв как закрытый
    db.set_feedback_status(fid, 1)

    await message.answer(f"Ответ отправлен и отзыв №{fid} закрыт.")
    await state.clear()
    
    
@admin_router.callback_query(F.data.startswith("reply_close:"))
async def start_reply_and_close(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    if not db.is_admin(user_id):
        await message.answer("🚫 У вас нет прав для доступа к админ-панели.")
        return

    _, fid_str = call.data.split(":", 1)
    try:
        fid = int(fid_str)
    except ValueError:
        await call.answer("Неверный id отзыва", show_alert=True)
        return

    target_user_id = db.get_feedback_user_id(fid)
    if target_user_id is None:
        await call.answer("Не удалось найти пользователя для этого отзыва", show_alert=True)
        return

    await state.update_data(reply_target_user_id=target_user_id, reply_feedback_id=fid)
    await state.set_state(SpecialistStates.waiting_for_answer_specialist)
    await call.message.edit_text("Введите текст ответа пользователю:")
    await call.answer()
    
# --- ПРОСМОТР ВСЕХ СООБЩЕНИЙ ---
@admin_router.callback_query(F.data == "show_all_feedbacks")
async def show_all_feedbacks(call: CallbackQuery):
    user_id = call.from_user.id
    if not db.is_admin(user_id):
        await message.answer("🚫 У вас нет прав для доступа к админ-панели.")
        return
    feedbacks = db.get_all_feedbacks()

    if not feedbacks:
        await call.message.edit_text("Задач не найдено.")
        await call.answer()
        return
    
    for fid, f_user_id, description, status in feedbacks:
        description = description or ""
        status_text = "незакрыто" if status == 0 else "закрыто"
        text = f"Отзыв №{fid}\nСтатус: {status_text}\nТекст: {description}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="☑️ Изменить статус", callback_data=f"change_status:{fid}")],
            [InlineKeyboardButton(text="🗑️ Удалить задачу", callback_data=f"delete_feedback:{fid}")],
            [InlineKeyboardButton(text="❌ Закрыть", callback_data=f"close_callback")]
        ])
        await call.message.answer(text, reply_markup=keyboard)
        await asyncio.sleep(0.05)
    
    await call.answer()
    

@admin_router.callback_query(F.data.startswith("change_status:"))
async def change_feedback_status(call: CallbackQuery):
    user_id = call.from_user.id
    if not db.is_admin(user_id):
        await message.answer("🚫 У вас нет прав для доступа к админ-панели.")
        return
    _, fid_str = call.data.split(":", 1)
    try:
        fid = int(fid_str)
    except ValueError:
        await call.answer("Неверный id отзыва", show_alert=True)
        return
    
    status = db.get_feedback_status(fid)
    if status is None:
        await call.answer("Отзыв не найден", show_alert=True)
        return

    new_status = 0 if status == 1 else 1
    db.set_feedback_status(fid, new_status)
    await call.message.edit_text(f"Статус отзыва №{fid} изменён на {'закрыт' if new_status == 1 else 'незакрыт'}.")
    await call.answer()
    
    
@admin_router.callback_query(F.data.startswith("delete_feedback:"))
async def delete_feedback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    if not db.is_admin(user_id):
        await message.answer("🚫 У вас нет прав для доступа к админ-панели.")
        return
    _, fid_str = call.data.split(":", 1)
    try:
        fid = int(fid_str)
    except ValueError:
        await call.answer("Неверный id отзыва", show_alert=True)
        return
    
    db.delete_feedback(fid)
    await call.message.edit_text(f"Отзыв №{fid} удалён.")
    await call.answer()
    

# --- ЛОГИКА РАССЫЛКИ ---
@admin_router.callback_query(F.data == "start_broadcast")
async def start_broadcast(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Отлично! Теперь отправьте мне сообщение для рассылки. Вы можете отправить текст, фото, видео или документ. Если хотите добавить URL-кнопку, укажите её в формате: `[Текст кнопки](URL)` в конце текста.")
    await state.set_state(SpecialistStates.waiting_for_broadcast_content)


@admin_router.message(SpecialistStates.waiting_for_broadcast_content)
async def process_broadcast_content(message: Message, state: FSMContext, bot: Bot):

    recipients = db.get_all_users()
    
    if not recipients:
        await message.answer("Не удалось найти получателей для рассылки.")
        await state.clear()
        return

    text = message.caption or message.text
    photo_id = message.photo[-1].file_id if message.photo else None
    video_id = message.video.file_id if message.video else None
    document_id = message.document.file_id if message.document else None
    url = None
    url_text = "Перейти"

    if text and text.count('](') == 1 and text.endswith(')'):
        try:
            url_text = text[text.rfind('[')+1:text.rfind(']')]
            url = text[text.rfind('(')+1:text.rfind(')')]
            text = text[:text.rfind('[')]
        except Exception:
            pass

    success_count = 0
    await message.answer("🚀 Начинаю рассылку...")
    
    for user_id in recipients:
        if await send_broadcast_message(bot, user_id, text, photo_id, video_id, document_id, url, url_text):
            success_count += 1
        await asyncio.sleep(0.5)

    await message.answer(f"✅ Рассылка завершена. Сообщение отправлено {success_count} из {len(recipients)} пользователей.")
    await state.clear()
    
    
# --- Отчет ---
@admin_router.callback_query(F.data == "generate_report")
async def generate_report_handler(call: CallbackQuery, bot: Bot):
    user_id = call.from_user.id
    if not db.is_admin(user_id):
        await message.answer("🚫 У вас нет прав для доступа к админ-панели.")
        return
    #await call.message.edit_text("📊 Генерирую отчёт, подождите...")

    try:
        bio, filename, summary = generate_report(db)  # как у тебя сейчас
        bio.seek(0)
        data_bytes = bio.read()
        await call.message.edit_text(summary)
        # Оборачиваем в BufferedInputFile (работает в том проекте, где у тебя уже есть пример)
        document = BufferedInputFile(data_bytes, filename=filename)
        
        await bot.send_document(chat_id=user_id, document=document)
        

    except Exception as e:
        await call.message.answer(f"❗ Ошибка при формировании отчёта: {e}")

    await call.answer()