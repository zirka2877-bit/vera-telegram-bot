import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
)

# === LINKS ===
GUIDE_URL = os.getenv(
    "GUIDE_URL",
    "https://drive.google.com/file/d/1ET0CazmAbpAR6ms8r-93krMY_EBScdqU/view?usp=sharing",
)
CONTACT_URL = os.getenv("CONTACT_URL", "https://t.me/itella")

WELCOME_TEXT = "Добро пожаловать!"

# === Keyboards ===
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
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть гайд (PDF)", url=GUIDE_URL)],
            [InlineKeyboardButton(text="Написать @itella", url=CONTACT_URL)],
        ]
    )

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Показать приветствие и кнопки"),
        BotCommand(command="restore", description="Вернуть кнопки внизу"),
        BotCommand(command="help", description="Что умеет бот"),
    ]
    try:
        await asyncio.wait_for(bot.set_my_commands(commands), timeout=5)
    except Exception as e:
        print(f"[warn] skip set_my_commands: {e}")

# === Handlers ===
async def on_start(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=reply_kb())
    await message.answer("Ваш гайд и быстрый контакт ниже:", reply_markup=inline_both())

async def on_restore(message: Message):
    await message.answer("Кнопки возвращены 👇", reply_markup=reply_kb())

async def on_help(message: Message):
    txt = (
        "Я показываю две постоянные кнопки внизу.\n\n"
        "• «Получить гайд 🎁» — пришлю кнопку со ссылкой на PDF\n"
        "• «Связаться со мной 📞✍️» — пришлю кнопку со ссылкой на чат\n\n"
        "Если кнопки пропали — команда /restore."
    )
    await message.answer(txt, reply_markup=reply_kb())

async def on_get_guide(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Открыть гайд (PDF)", url=GUIDE_URL)]]
    )
    await message.answer("Нажмите кнопку ниже, чтобы открыть гайд:", reply_markup=kb)

async def on_contact(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Написать @itella", url=CONTACT_URL)]]
    )
    await message.answer("Напишите мне — кнопка ниже:", reply_markup=kb)

# Ловим любое иное сообщение — возвращаем клавиатуру
async def on_any(message: Message):
    await message.answer("Клавиатура активна 👇", reply_markup=reply_kb())

# === Entry point ===
async def main():
    token = (os.getenv("BOT_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("Переменная окружения BOT_TOKEN не задана.")
    bot = Bot(token=token)
    dp = Dispatcher()

    dp.message.register(on_start, CommandStart())
    dp.message.register(on_restore, Command("restore"))
    dp.message.register(on_help, Command("help"))
    dp.message.register(on_get_guide, F.text == "Получить гайд 🎁")
    dp.message.register(on_contact, F.text == "Связаться со мной 📞✍️")
    dp.message.register(on_any)  # последним — ловит всё остальное

    # не блокируем запуск, если сеть «подвиснет»
    asyncio.create_task(set_commands(bot))

    print("Bot is running (long polling).")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
