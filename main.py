import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from db import create_table, set_db_name as set_db_name_db
from handlers import register_handlers, set_db_name as set_db_name_handlers

API_TOKEN = '7097172213:AAE5RGy_Z7xt3M7i0s6vKYmN3s7B9zdH_fI'
DB_NAME = 'quiz_bot.db'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

set_db_name_db(DB_NAME)
set_db_name_handlers(DB_NAME)

register_handlers(dp)

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
#