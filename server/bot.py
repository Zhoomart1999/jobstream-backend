import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@job_kg_channel" # Placeholder

bot = None
if TOKEN and ":" in TOKEN: # Basic check for valid-looking token
    try:
        from aiogram.utils.token import validate_token
        validate_token(TOKEN)
        bot = Bot(token=TOKEN)
    except:
        pass

dp = Dispatcher()

async def post_vacancy_to_channel(title: str, salary: str, location: str, url: str):
    if not bot:
        logging.warning("Telegram Bot is not initialized. Skipping post.")
        return False
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="СМОТРЕТЬ ВАКАНСИЮ", url=url))
    
    text = (
        f"🔥 **НОВАЯ ВАКАНСИЯ: {title}**\n\n"
        f"📍 Город: {location}\n"
        f"💰 Зарплата: {salary}\n\n"
        f"👉 Откликнуться в приложении JobStream"
    )
    
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=builder.as_markup()
        )
        return True
    except Exception as e:
        logging.error(f"Error posting to TG: {e}")
        return False
