from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import orm_get_channels


async def adm_menu_kb():
    markup = InlineKeyboardBuilder()

    markup.add(InlineKeyboardButton(text='🌐 Модерация постов', callback_data='moder_posts'))
    markup.row(InlineKeyboardButton(text='📊 Статистика', callback_data='adm_stat'))
    markup.add(InlineKeyboardButton(text='📋 Рассылка', callback_data='multi_message'))
    markup.row(InlineKeyboardButton(text='💰 Добавить таргет подписку', callback_data='add_channel'))
    markup.add(InlineKeyboardButton(text='🗑️ Удалить таргет подписку', callback_data='delete_channel'))
    markup.row(InlineKeyboardButton(text='📥 Бэкап БД', callback_data='backup_bd'))
    markup.row(InlineKeyboardButton(text='Меню', callback_data='back_menu'))

    result = markup.as_markup()

    return result

async def adm_multi_kb():
    markup = InlineKeyboardBuilder()
    
    markup.add(InlineKeyboardButton(text='📈Таргет', callback_data='target'))
    markup.row(InlineKeyboardButton(text='✉️Обычная рассылка', callback_data='defualt_multi'))

    result = markup.as_markup()

    return result


async def adm_delete_chanel_kb(session):
    markup = InlineKeyboardBuilder()
    data = await orm_get_channels(session)

    for id, channel in enumerate(data):
        markup.row(InlineKeyboardButton(text=f'{id+1} - {channel.channel_name}', callback_data=f'delete_{channel.id}'))

    markup.row(InlineKeyboardButton(text='<< Назад', callback_data='adm_menu'))
    return markup.as_markup()

