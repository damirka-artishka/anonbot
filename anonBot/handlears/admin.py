from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery,  InlineKeyboardButton
from aiogram.types.input_file import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import DB_LITE
from database.requests import orm_check_registration, orm_get_post, orm_info_post, orm_get_post_to_publich, orm_delete_post, orm_get_count_posts, orm_add_count_post, orm_edit_post, orm_get_all_posts, orm_get_all_users, orm_get_all_user_ids, orm_delete_user, orm_add_channel, orm_delete_channel

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.enums import ParseMode

from Keyboards.adminkb import adm_menu_kb, adm_multi_kb, adm_delete_chanel_kb

admin_router = Router()

@admin_router.callback_query(F.data.startswith('adm_menu'))
async def adm_menu_callback(callback: CallbackQuery, session: AsyncSession):
    data = await orm_check_registration(session, callback.from_user.id)

    if data.admin_status:
        await callback.message.edit_text(text='Вот админ меню', reply_markup=await adm_menu_kb())



@admin_router.message(Command('adm'))
async def adm_menu(message: Message, session: AsyncSession, bot: Bot):
    data = await orm_check_registration(session, message.from_user.id)
    if data.admin_status:
        await bot.send_message(chat_id=message.from_user.id, text='Вот админ меню', reply_markup=await adm_menu_kb())



@admin_router.callback_query(F.data.startswith('moder_posts'))
async def moder_post(callback: CallbackQuery, session: AsyncSession):
    data = await orm_get_post(session)
    markup = InlineKeyboardBuilder()
    await callback.message.delete()
    for post in data[::-1]:
        markup.row(InlineKeyboardButton(text=f'{post.description[:20]}... | {post.date}', callback_data=f'moder_post_{post.id}'))
    markup.row(InlineKeyboardButton(text='Назад', callback_data='adm_menu'))
    result = markup.as_markup()
    await callback.message.answer(f'Посты ожидающие модерации', reply_markup=result)


#   Процесс модерации поста
@admin_router.callback_query(F.data.startswith('moder_post_'))
async def info_post(callback: CallbackQuery, session: AsyncSession):
    markup = InlineKeyboardBuilder()
    data = await orm_info_post(session, callback.data.split('moder_post_')[1])

    markup.row(InlineKeyboardButton(text='Редактировать', callback_data=f'edit_post_{data[0].id}'))
    markup.row(InlineKeyboardButton(text='Одобрить', callback_data=f'succes_post_{data[0].id}'))
    markup.add(InlineKeyboardButton(text='Отклонить', callback_data=f'not_succes_post_{data[0].id}'))

    markup.row(InlineKeyboardButton(text='Предыдущий', callback_data=f'back_post_{int(data[0].id)+1}'))

    markup.add(InlineKeyboardButton(text='Назад', callback_data='moder_posts'))

    markup.add(InlineKeyboardButton(text='Следущий', callback_data=f'go_post_{int(data[0].id)-1}'))

    
    result = markup.as_markup() 

    if data[0].status == 'Не анонимно':
        data[0].status = data[0].tg_tag

    await callback.message.edit_text(text=f"Anon Shymkent🍁\n\n• {data[0].description}\n\nИсточник - {data[0].status}\n\nСтатус - ожидается одобрения⏳\n\nАвтор поста - {data[0].tg_tag}", reply_markup=result)

#   Процесс одобрения поста
@admin_router.callback_query(F.data.startswith('succes_post_'))
async def publick_post(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    data = await orm_get_post_to_publich(session, callback.data.split('succes_post_')[1])

    markup = InlineKeyboardBuilder()

    markup.add(InlineKeyboardButton(text='Предыдущий', callback_data=f'back_post_{int(callback.data.split('succes_post_')[1])-1}'))
    markup.add(InlineKeyboardButton(text='Следущий', callback_data=f'go_post_{int(callback.data.split('succes_post_')[1])+1}'))

    markup.row(InlineKeyboardButton(text='Назад', callback_data='moder_posts'))
    result = markup.as_markup()

    date = await orm_get_count_posts(session, callback.from_user.id)
    user_id = await orm_get_post_to_publich(session, callback.data.split('succes_post_')[1])
    bot_username = await bot.get_me()
    if data.status == 'Не анонимно':
        data.status = data.tg_tag
    if data.photo != 'None':
        await bot.send_photo(chat_id='-1002381057156', photo=data.photo, caption=f"Anon Shymkent🍁\n\n• {data.description}\n\nИсточник - {data.status}\n\n--------------------\nНаписать анонимку - @{bot_username.username}")
    else:
        await bot.send_message(chat_id='-1002381057156', text=f"Anon Shymkent🍁\n\n• {data.description}\n\nИсточник - {data.status}\n\nНаписать анонимку - @{bot_username.username}")

    await bot.send_message(chat_id=user_id.tg_id, text='✅Ваша анонимка была одобрена!')
    await orm_delete_post(session, callback.data.split('succes_post_')[1])
    await orm_add_count_post(session, callback.from_user.id, date.count_all_posts-1)

    await callback.message.edit_text(text='Успешно!', reply_markup=result)




@admin_router.callback_query(F.data.startswith('not_succes_post_'))
async def not_succes_post(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    date = await orm_get_count_posts(session, callback.from_user.id)
    await orm_add_count_post(session, callback.from_user.id, date.count_all_posts-1)
    user_id = await orm_get_post_to_publich(session, callback.data.split('not_succes_post_')[1])
    await bot.send_message(chat_id=user_id.tg_id, text='❌Ваша анонимка была отклонена')

    await orm_delete_post(session, callback.data.split('not_succes_post_')[1])

    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Назад', callback_data='moder_posts'))
    result = markup.as_markup()
    await callback.message.edit_text(text='Успешно!', reply_markup=result)


@admin_router.callback_query(F.data.startswith('adm_stat'))
async def stat(callback: CallbackQuery, session: AsyncSession):
    stat_users = await orm_get_all_users(session)
    stat_posts = await orm_get_all_posts(session)

    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='Назад', callback_data='adm_menu'))
    result = markup.as_markup()

    await callback.message.edit_text(text=f'Статистика\n\nОбщее кол-во всех пользователей - {stat_users}\nОбщее кол-во постов в ожидании модерации - {stat_posts}', reply_markup=result)


@admin_router.callback_query(F.data.startswith('go_post_'))
async def go_post(callback: CallbackQuery, session: AsyncSession):
    try:
        data = await orm_info_post(session, callback.data.split('go_post_')[1])

        markup = InlineKeyboardBuilder()

        markup.row(InlineKeyboardButton(text='Редактировать', callback_data=f'edit_post_{data[0].id}'))
        markup.row(InlineKeyboardButton(text='Одобрить', callback_data=f'succes_post_{data[0].id}'))
        markup.add(InlineKeyboardButton(text='Отклонить', callback_data=f'not_succes_post_{data[0].id}'))

        markup.row(InlineKeyboardButton(text='Предыдущий', callback_data=f'back_post_{int(data[0].id)+1}'))

        markup.add(InlineKeyboardButton(text='Назад', callback_data='moder_posts'))

        markup.add(InlineKeyboardButton(text='Следущий', callback_data=f'go_post_{int(data[0].id)-1}'))

    
        result = markup.as_markup() 

        if data[0].status == 'Не анонимно':
            data[0].status = data[0].tg_tag

        await callback.message.edit_text(text=f"Anon Shymkent🍁\n\n• {data[0].description}\n\nИсточник - {data[0].status}\n\nСтатус - ожидается одобрения⏳\n\nАвтор поста - {data[0].tg_tag}", reply_markup=result)
    except:
        await callback.answer()
 
@admin_router.callback_query(F.data.startswith('back_post_'))
async def go_post(callback: CallbackQuery, session: AsyncSession):
    try:
        data = await orm_info_post(session, callback.data.split('back_post_')[1])

        markup = InlineKeyboardBuilder()
    
        markup.row(InlineKeyboardButton(text='Редактировать', callback_data=f'edit_post_{data[0].id}'))
        markup.row(InlineKeyboardButton(text='Одобрить', callback_data=f'succes_post_{data[0].id}'))
        markup.add(InlineKeyboardButton(text='Отклонить', callback_data=f'not_succes_post_{data[0].id}'))

        markup.row(InlineKeyboardButton(text='Предыдущий', callback_data=f'back_post_{int(data[0].id)+1}'))

        markup.add(InlineKeyboardButton(text='Назад', callback_data='moder_posts'))

        markup.add(InlineKeyboardButton(text='Следущий', callback_data=f'go_post_{int(data[0].id)-1}'))

    
        result = markup.as_markup() 

        if data[0].status == 'Не анонимно':
            data[0].status = data[0].tg_tag

        await callback.message.edit_text(text=f"Anon Shymkent🍁\n\n• {data[0].description}\n\nИсточник - {data[0].status}\n\nСтатус - ожидается одобрения⏳\n\nАвтор поста - {data[0].tg_tag}", reply_markup=result)
    except:
        await callback.answer()


@admin_router.callback_query(F.data.startswith('delete_channel'))
async def start_delete_channel(callback: CallbackQuery, session: AsyncSession):
    await callback.message.edit_text(text='🗑️ Выбери канал который нужно удалить из таргета...', reply_markup=await adm_delete_chanel_kb(session))


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_channel(callback: CallbackQuery, session: AsyncSession):
    await orm_delete_channel(session, callback.data.split('delete_')[1])
    
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text='<< Назад', callback_data='delete_channel'))
    result = markup.as_markup()

    await callback.message.edit_text('Удалено!', reply_markup=result)

@admin_router.callback_query(F.data.startswith('backup_bd'))
async def backup_bd(callback: CallbackQuery, bot: Bot):
    backup = FSInputFile(DB_LITE.split('sqlite+aiosqlite:///')[1])

    await bot.send_document(chat_id = callback.from_user.id, document=backup)


#! FSM 


class EditPost(StatesGroup):
    post_id = State()
    description = State()


@admin_router.callback_query(StateFilter(None), F.data.startswith('edit_post_'))
async def get_desc(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите отредактированное описание анонимки')
    await state.update_data(post_id=callback.data.split('edit_post_')[1])
    await state.set_state(EditPost.description)


@admin_router.message(EditPost.description, F.text)
async def edit_post(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await orm_edit_post(session, data['post_id'], data['description'])

    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text='Вернутся к посту', callback_data=f'moder_post_{data['post_id']}'))
    result=markup.as_markup()

    await message.answer('Изменино!', reply_markup=result)
    await state.clear()


@admin_router.callback_query(F.data.startswith('multi_message'))
async def use_multi(callback: CallbackQuery):
    await callback.message.edit_text(text='📜Выбери тип рассылки...', reply_markup=await adm_multi_kb())


#! FSM Edit Post

class AddChannel(StatesGroup):
    link = State()


@admin_router.callback_query(StateFilter(None), F.data.startswith('add_channel'))
async def link_get(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('✍️Введи ссылку на канал (полную ссылку)...')
    
    await state.set_state(AddChannel.link)


@admin_router.message(AddChannel.link, F.text)
async def add_channel_target(message: Message, session: AsyncSession, bot: Bot, state: FSMContext):
    await state.update_data(link=message.text)
    data = await state.get_data()

    channel_name = await bot.get_chat(f"@{message.text}")
    await orm_add_channel(session, {
        "channel_name": channel_name.title,
        "url": message.text,
        "owner_id": message.from_user.id,
        "limit": 100
    })
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text='Назад', callback_data='adm_menu'))
    result = markup.as_markup()

    await message.answer(f'Канал <<{channel_name.title}>>\n\nУспено добавлен!', reply_markup=result)




class DefualtMulti(StatesGroup):
    text = State()
    topic = State()


@admin_router.callback_query(StateFilter(None), F.data.startswith('defualt_multi'))
async def defualt_multi(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('📝Введите тему для рассылки...')

    await state.set_state(DefualtMulti.topic)

@admin_router.message(DefualtMulti.topic, F.text)
async def topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await message.answer('📝Введите текст для рассылки...')

    await state.set_state(DefualtMulti.text)

@admin_router.message(DefualtMulti.text, F.text)
async def go_defualt_multi(message: Message, session: AsyncSession, bot: Bot, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    user_ids = await orm_get_all_user_ids(session)
    markup = InlineKeyboardBuilder()

    markup.add(InlineKeyboardButton(text='📋Отправить рассылку', callback_data='start_defualt_multi'))

    result = markup.as_markup()

    await message.answer(text=f'🤖 Уведомление от бота: Ваша рассылка готова к отправке\nЗдравствуйте, {message.from_user.first_name}!\n\nВаше сообщение готово к отправке пользователям. Вот основные детали:\n\n📬 Тема рассылки: <b>{data['topic']}</b> \n👥 Получатели: <b>{len(user_ids)}</b>\n\nСодержание рассылки: <b>{data['text']}</b>\n\nПожалуйста, подтвердите, что все данные верны. Если вы хотите внести изменения, просто дайте мне знать!\n\n✅ Для отправки нажмите: [Кнопка: Отправить рассылку]\n\nС уважением, Ваш\nпомощник-бот!', reply_markup=result, parse_mode=ParseMode.HTML)

@admin_router.callback_query(DefualtMulti.text, F.data.startswith('start_defualt_multi'))
async def start_defualt_multi(callback: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext):

    data = await state.get_data()

    user_ids = await orm_get_all_user_ids(session)

    await callback.message.answer('Рассылка началась')

    markup = InlineKeyboardBuilder()

    markup.add(InlineKeyboardButton(text='♨️Понятно♨️', callback_data='clear'))

    result = markup.as_markup()


    for user in user_ids:
        try:
            await bot.send_message(chat_id=user.tg_id, text=f'<b>{data['topic']}</b>\n\n<i>{data['text']}</i>', reply_markup=result, parse_mode=ParseMode.HTML)
        except:
            pass

    await state.clear()

    await callback.message.answer('Рассылка закончилась')

@admin_router.callback_query(F.data.startswith('clear'))
async def clear(callback: CallbackQuery):
    await callback.message.delete()

#! FSM multi_message_target

class MultiMessage(StatesGroup):
    topic = State()
    text = State()
    text_btn = State()
    ref_link = State()

@admin_router.callback_query(StateFilter(None), F.data.startswith('target'))
async def defualt_multi(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer('📝Введите тему для рассылки...')

    await state.set_state(MultiMessage.topic)

@admin_router.message(MultiMessage.topic, F.text)
async def topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await message.answer('📝Введите текст для рассылки...')

    await state.set_state(MultiMessage.text)


@admin_router.message(MultiMessage.text, F.text)
async def ref_link(message: Message, state: FSMContext):
    await state.update_data(text=message.text)


    await message.answer('📝Введите реферальную ссылку')

    await state.set_state(MultiMessage.ref_link)



@admin_router.message(MultiMessage.ref_link, F.text)
async def ref_link(message: Message, state: FSMContext):
    await state.update_data(ref_link=message.text)

    await message.answer('📝Введите название кнопки')

    await state.set_state(MultiMessage.text_btn)


@admin_router.message(MultiMessage.text_btn, F.text)
async def start_multi_message(message: Message, session: AsyncSession, bot: Bot, state: FSMContext):
    await state.update_data(text_btn=message.text)
    data = await state.get_data()

    user_ids = await orm_get_all_user_ids(session)

    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text=data['text_btn'], url=data['ref_link']))
    result = markup.as_markup()

    await message.answer('Рассылка началась')

    for user in user_ids:
        try:
            await bot.send_message(chat_id=user.tg_id, text=f'<b>{data['topic']}</b>\n\n<i>{data['text']}</i>', reply_markup=result, parse_mode=ParseMode.HTML)
        except:
            pass

    await state.clear()

    await message.answer('Рассылка закончилась')



