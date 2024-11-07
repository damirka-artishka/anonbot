from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from localisation.russian import menu_kb, post_photo_btns

async def menu():
    markup = InlineKeyboardBuilder()

    markup.add(InlineKeyboardButton(text=menu_kb['publications'], callback_data='publications'))
    markup.add(InlineKeyboardButton(text=menu_kb['publich'], callback_data='publich'))
    markup.row(InlineKeyboardButton(text=menu_kb['faq'], callback_data='faq'))

    result = markup.as_markup()

    return result

async def post_photo_btn(status):
    markup = InlineKeyboardBuilder()

    if status == 'defoult':
        markup.add(InlineKeyboardButton(text=post_photo_btns['anon'], callback_data='anon'))
        markup.add(InlineKeyboardButton(text=post_photo_btns['not_anon'], callback_data='not_anon'))
        markup.row(InlineKeyboardButton(text=post_photo_btns['publich'], callback_data='publich'))
    elif status == 'anon':
        markup.add(InlineKeyboardButton(text=f'🤫{post_photo_btns['anon']}', callback_data='anon'))
        markup.add(InlineKeyboardButton(text=post_photo_btns['not_anon'], callback_data='not_anon'))
        markup.row(InlineKeyboardButton(text=post_photo_btns['publich'], callback_data='publich'))
    else:
        markup.add(InlineKeyboardButton(text=post_photo_btns['anon'], callback_data='anon'))
        markup.add(InlineKeyboardButton(text=f'👤{post_photo_btns['not_anon']}', callback_data='not_anon'))
        markup.row(InlineKeyboardButton(text=post_photo_btns['publich'], callback_data='publich'))

    result = markup.as_markup()

    return result



async def no_photo_btn():
    markup = InlineKeyboardBuilder()

    markup.add(InlineKeyboardButton(text='У меня нету фотографии', callback_data='no_photo'))

    result = markup.as_markup()

    return result


