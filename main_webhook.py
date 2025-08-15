import os
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    BotCommand, Update,
)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

GUIDE_URL   = os.getenv("GUIDE_URL", "https://drive.google.com/file/d/1ET0CazmAbpAR6ms8r-93krMY_EBScdqU/view?usp=sharing")
CONTACT_URL = os.getenv("CONTACT_URL", "https://t.me/itella")
WELCOME_TEXT = "Добро пожаловать!"

bot = Bot(BOT_TOKEN)
dp  = Dispatcher()

def reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Получить гайд 🎁")],
            [KeyboardButton(text="Связаться со мной 📞✍️")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )

def inline_both() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть гайд (PDF)", url=GUIDE_URL)],
        [InlineKeyboardButton(text="Написать @itella", url=CONTACT_URL)],
    ])

def inline_for_guide() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть гайд (PDF)", url=GUIDE_URL)]
    ])

def inline_for_contact() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Написать @itella", url=CONTACT_URL)]
    ])

async def set_commands():
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Показать приветствие и кнопки"),
            BotCommand(command="restore", description="Вернуть кнопки внизу"),
            BotCommand(command="help", description="Что умеет бот"),
        ])
    except Exception as e:
        print("[warn] set_my_commands:", e)

async def h_start(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=reply_kb())
    await message.answer("Ваш гайд и быстрый контакт ниже:", reply_markup=inline_both())

async def h_restore(message: Message):
    await message.answer("Кнопки возвращены 👇", reply_markup=reply_kb())

async def h_help(message: Message):
    txt = (
        "Я показываю две постоянные кнопки внизу.\n\n"
        "Нажмите:\n"
        "• «Получить гайд 🎁» — пришлю кнопку со ссылкой на PDF\n"
        "• «Связаться со мной 📞✍️» — пришлю кнопку со ссылкой на чат\n\n"
        "Если кнопки пропали — команда /restore."
    )
    await message.answer(txt, reply_markup=reply_kb())

async def h_get_guide(message: Message):
    await message.answer("Нажмите кнопку ниже, чтобы открыть гайд:", reply_markup=inline_for_guide())

async def h_contact(message: Message):
    await message.answer("Напишите мне — кнопка ниже:", reply_markup=inline_for_contact())

async def h_any(message: Message):
    await message.answer("Клавиатура активна 👇", reply_markup=reply_kb())

dp.message.register(h_start,    CommandStart())
dp.message.register(h_restore,  Command("restore"))
dp.message.register(h_help,     Command("help"))
dp.message.register(h_get_guide, F.text == "Получить гайд 🎁")
dp.message.register(h_contact,   F.text == "Связаться со мной 📞✍️")
dp.message.register(h_any)

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await set_commands()

@app.get("/")
async def health():
    return {"ok": True}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}
