# menu/start_menu
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from menu.keyboard import start_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from db_manager.db import Database

menu_router = Router()
db = Database()


@menu_router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.delete()
    user_id = message.from_user.id
    if not db.user_exists(user_id):
        db.add_user(user_id)

    await message.answer(
        "Добро пожаловать в бот обратной связи компании <b>Мед-интерпласт!</b>💙\n\n"
        "Мы ценим ваше мнение и стремимся к постоянному улучшению!\n\n"
        "Пожалуйста, поделитесь с нами вашим предложением или замечанием.",
        reply_markup=start_keyboard(),
        parse_mode="HTML"
    )


@menu_router.message(F.text == '/help')
async def user_help_handler(message: Message):
    await message.delete()
    await message.answer(
    "Мы на связи для вас!\n\n"
    "Если у вас есть замечание или идея для улучшения рабочих процессов, а может просто хотите поделиться своим мнением — напишите нам.\n"
    "Спасибо, что помогаете нам становиться лучше! ❤️\n\n"
    )