import asyncio

from database.engine import DataBaseSession
from config import TOKEN
#from localisation.russian import start


from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import Dispatcher, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode


from handlears.handlear import router
from handlears.admin import admin_router

from database.requests import orm_add_channel, orm_get_channels, orm_check_registration, orm_registartion
from database.engine import create_db, session_maker

from Keyboards.keyboard_user import menu

from localisation.russian import photos


bot = Bot(token=TOKEN)
dp = Dispatcher()



async def main():
    await create_db()
    dp.include_router(router)
    dp.include_router(admin_router)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    print("[+] DataBase")
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except:
        print('[-] Бот лег!')



if __name__ == '__main__':
    asyncio.run(main())



