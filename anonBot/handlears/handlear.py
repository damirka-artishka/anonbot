from typing import Text
from aiogram import F, Router, Dispatcher
from aiogram import Bot
from aiogram.types import Message, CallbackQuery,  InlineKeyboardButton
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.methods import GetChatMember
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession


from Keyboards.keyboard_user import menu, post_photo_btn, no_photo_btn
from database.requests import orm_add_post, orm_registartion, orm_check_registration, orm_add_channel, orm_get_channels, orm_get_post, orm_get_posts, orm_info_post, orm_get_count_posts, orm_add_count_post, orm_get_admins, orm_edit_post

from localisation.russian import photos

router = Router()


#! Начало регистрации

#Функ. проверяет на подписку 
async def check_subscribtion(message, session, bot):
    status = 'False'
    for channel in await orm_get_channels(session):
        user_channel_status = await bot.get_chat_member(chat_id=f"@{channel.url}", user_id=message.from_user.id)
        if user_channel_status.status != 'left':
            status = 'True'
        else:
            status = 'False'
    return status   
async def check(message, session, bot: Bot):
    global mess
    if await check_subscribtion(message, session, bot) != 'True':
        markup = InlineKeyboardBuilder()
        data = await orm_get_channels(session)
        for i in data:
            markup.row(InlineKeyboardButton(text=i.channel_name, callback_data=str(i.id), url=f'https://t.me/{i.url}'))
        markup.row(InlineKeyboardButton(text='Проверить подписку', callback_data='check'))
        kb = markup.as_markup()
        mess = await message.answer(text="Чтобы использовать бота подпишись на каналы ниже!", reply_markup=kb)
        return False
    try:
        await message.answer_photo(photo=photos, caption=f'🌟 Привет, {message.from_user.first_name}!  \nОставьте свой пост — анонимно 🙈 или с указанием имени 👤. \n\n<i>✨ • Даже администраторы не смогут узнать, что именно ВЫ написали в анонимном посте.  \n⚡️ • Анонимные сообщения публикуются здесь быстрее, чем в нашем Instagram-аккаунте.  \n🔒 • О конфиденциальности не стоит беспокоиться.</i>\n\n🤔 Какой вариант вы выбираете?  \n\n🎉💬', reply_markup=await menu(), parse_mode=ParseMode.HTML)
    except:
        await message.message.answer_photo(photo=photos, caption=f'🌟 Привет, {message.from_user.first_name}!  \nОставьте свой пост — анонимно 🙈 или с указанием имени 👤. \n\n<i>✨ • Даже администраторы не смогут узнать, что именно ВЫ написали в анонимном посте.  \n⚡️ • Анонимные сообщения публикуются здесь быстрее, чем в нашем Instagram-аккаунте.  \n🔒 • О конфиденциальности не стоит беспокоиться.</i>\n\n🤔 Какой вариант вы выбираете?  \n\n🎉💬', reply_markup=await menu(), parse_mode=ParseMode.HTML)
 
    return True

#Хэндлер ловит нажатие кнопки 'Проверить подписку'
@router.callback_query(F.data.startswith('check'))
async def check_btn(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    if await check(callback, session, bot):
        await callback.message.delete()
        

#Хэндлер ловит команду /start
@router.message(CommandStart())
async def registration (message: Message, session: AsyncSession, bot: Bot):
    res = await orm_check_registration(session, message.from_user.id)
    admin = False
    if res is None:
        if message.from_user.id == 1936623121:
            admin = True
        await orm_registartion(session, {
                "tg_id" : message.from_user.id,
                "tag" : message.from_user.username,
                "premium_status" : False,
                "admin_status" : admin,
                "moder_status": False,
                "stars" : 0,
                "count_all_posts" : 0})
        
    await check(message, session, bot)
        
#! Конец регистрации




@router.callback_query(F.data.startswith('faq'))
async def faq(callback: CallbackQuery, session: AsyncSession):
    markup = InlineKeyboardBuilder()

    markup.add(InlineKeyboardButton(text='Назад', callback_data='back_menu'))

    result = markup.as_markup()
    await callback.message.delete()
    await callback.message.answer(text='👻 Не стесняйтесь делиться своими идеями, вопросами или предложениями! 💡✨\n\n💬 Как это работает?  \n\n1. Нажмите в меню [ /start ] и выберите кнопку "Написать анонимку" 📝.\n\n2. Напишите текст для своей анонимки. ✍️\n\n3. Отправьте изображение (если таково имеется) 🖼.\n\n4. Выберите, хотите ли вы оставить его анонимным или сделать НЕ анонимным 🤫/👤.\n\n5. Нажмите "Отправить" и ждите публикации! ⏳\n\n📢Поделитесь с друзьями!\nРасскажите о нашем проекте своим друзьям и знакомым. Чем больше участников — тем интереснее обсуждения! 🤗🎉', reply_markup=result)




@router.callback_query(F.data.startswith('publications'))
async def publications(callback: CallbackQuery, session: AsyncSession):
    data = await orm_get_posts(session, callback.from_user.id)
    markup = InlineKeyboardBuilder()
    await callback.message.delete()

    for id, post in enumerate(data[::-1]):
        markup.row(InlineKeyboardButton(text=f'{id+1} - {post.description[:20]}... | {post.date}', callback_data=f'post_{post.id}'))
    markup.row(InlineKeyboardButton(text='<- Назад', callback_data='back_menu'))

    result = markup.as_markup()
    text = 'Вот твои анонимные сообщения! 😊\n\n• Нажми на любую анонимку и посмотри, как она выглядит.🔍'
    if len(data) < 1:
        text = 'Ой-ой-ой, похоже, тут пусто! 😅✨'
    await callback.message.answer(text, reply_markup=result)



@router.callback_query(F.data.startswith('post_'))
async def info_post(callback: CallbackQuery, session: AsyncSession):
    markup = InlineKeyboardBuilder()
    data = await orm_info_post(session, callback.data.split('post_')[1])

    markup.row(InlineKeyboardButton(text='✏️ Редактировать', callback_data=f'edit_post_user_{callback.data.split('post_')[1]}'))
    markup.row(InlineKeyboardButton(text='<- Назад', callback_data='publications'))

    result = markup.as_markup() 
    if data[0].status == 'Не анонимно':
        data[0].status = data[0].tg_tag
    await callback.message.edit_text(text=f"Anon Shymkent🍁\n\n• {data[0].description}\n\nИсточник - {data[0].status}\n\nСтатус - ожидает одобрения⏳", reply_markup=result)



@router.callback_query(F.data.startswith('back_menu'))
async def back_menu(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    await callback.message.delete()
    await callback.message.answer_photo(photo=photos, caption=f'🌟 Привет, {callback.from_user.first_name}!  \nОставьте свой пост — анонимно 🙈 или с указанием имени 👤. \n\n<i>✨ • Даже администраторы не смогут узнать, что именно вы написали в анонимном посте.  \n⚡️ • Анонимные сообщения публикуются здесь быстрее, чем в нашем Instagram-аккаунте.  \n🔒 • О конфиденциальности не стоит беспокоиться.</i>\n\n🤔 Какой вариант вы выбираете?  \n\n🎉💬', reply_markup=await menu(), parse_mode=ParseMode.HTML)






#! FSM

class EditPostUser(StatesGroup):
    post_id = State()
    description = State()


@router.callback_query(StateFilter(None), F.data.startswith('edit_post_user_'))
async def get_desc(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите отредактированное описание анонимки. ✍️')
    await state.update_data(post_id=callback.data.split('edit_post_user_')[1])
    await state.set_state(EditPostUser.description)


@router.message(EditPostUser.description, F.text)
async def edit_post(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    await orm_edit_post(session, data['post_id'], data['description'])

    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text='📖 Вернутся к посту', callback_data=f'post_{data['post_id']}'))
    result=markup.as_markup()

    await message.answer('Анонимка отредактирована! ✅', reply_markup=result)
    await state.clear()

class AddPost(StatesGroup):
    tg_id = State()
    tg_user = State()
    description = State()
    photo = State()
    status = State()






@router.callback_query(StateFilter(None), F.data.startswith('publich'))
async def publich_post(callback: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext):
    data = await orm_get_count_posts(session, callback.from_user.id)
    if data.count_all_posts <6 and data.count_all_posts != 5:
        #await bot.delete_message(chat_id=callback.message.from_user.id, message_id=callback.message.message_id)
        await callback.message.delete()
        await callback.message.answer('Напишите текст для своей анонимки. ✍️')

        await state.set_state(AddPost.description)
    else:
        await callback.message.answer('Ты превысил максимальное кол-во постов\n\nДождись одобрения предыдущих постов', reply_markyp=await menu())
        
        await state.clear()



@router.message(AddPost.description, F.text)
async def post_photo(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(description=message.text)
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(tg_user=f'@{message.from_user.username}')
    result = await state.get_data()
    await message.answer(f'Вот так вот выглядит твоя анонимка:\n\nAnon Shymkent🍁\n\n• {result['description']}\n\n—————————-\nОтправьте изображение (если таково имеется) 🖼.', reply_markup=await no_photo_btn())

    await state.set_state(AddPost.photo)

@router.callback_query(AddPost.photo, F.data.startswith('no_photo'))
async def no_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await state.update_data(photo='None')
    data = await state.get_data()
    await callback.message.edit_text(f'Вот так вот выглядит твоя анонимка:\n\nAnon Shymkent🍁\n\n• {data['description']}\n\n—————————-\nВыберите, хотите ли вы оставить его анонимным или НЕ анонимно 🤫/👤.', reply_markup=await post_photo_btn('defoult'))

    await state.set_state(AddPost.status)



@router.message(AddPost.photo, F.photo)
async def post_status(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    data = await state.get_data()
    await message.delete()
    await bot.send_photo(chat_id=message.from_user.id, photo=message.photo[-1].file_id, caption=f'Вот так вот выглядит твоя анонимка:\n\nAnon Shymkent🍁\n\n• {data['description']}\n\n—————————-\nВыберите, хотите ли вы оставить его анонимным или сделать  НЕ анонимным 🤫/👤.', reply_markup=await post_photo_btn('defoult'))

    await state.set_state(AddPost.status)

@router.callback_query(AddPost.status, F.data.startswith('anon'))
async def post_anawaiton_status(callback: CallbackQuery, state: FSMContext):
    await state.update_data(status='Анонимно')
    await callback.message.edit_reply_markup(reply_markup=await post_photo_btn('anon'))

@router.callback_query(AddPost.status, F.data.startswith('not_anon'))
async def post_not_anon_status(callback: CallbackQuery, state: FSMContext):
    await state.update_data(status='Не анонимно')
    await callback.message.edit_reply_markup(reply_markup=await post_photo_btn('not_anon'))

@router.callback_query(AddPost.status, F.data.startswith('publich'))
async def publich_post(callback: CallbackQuery, session: AsyncSession, bot: Bot, state: FSMContext):
    markup = InlineKeyboardBuilder()
    data = await state.get_data()
    markup.add(InlineKeyboardButton(text='Назад в меню', callback_data='back_menu'))
    result = markup.as_markup() 
    try:
        await orm_add_post(session, {
            "description": data['description'],
            "tg_id": data['tg_id'],
            "tg_tag": data['tg_user'],
            "premium": False,
            "photo": data['photo'],
            "status": data['status'],
        })
        date = await orm_get_count_posts(session, callback.from_user.id)
        await orm_add_count_post(session, callback.from_user.id, date.count_all_posts+1)
        await callback.message.delete()
        
        if data['status'] == 'Не анонимно':
            data['status'] = data['tg_user']

        if data['photo'] != 'None':
            await bot.send_photo(chat_id=callback.from_user.id, photo=data['photo'],  caption=f'✅ Отлично!\n🎉 Отправлено на модерацию\n--------\nВот так выглядит твоя анкета:\n\nAnon Shymkent🍁\n\n• {data['description']}\n\nИсточник - {data['status']}\n--------\nСтатус - ожидает одобрения⏳', reply_markup=result)
        else:
            await callback.message.answer(f'✅ Отлично!\n 🎉 Отправлено на модерацию\n--------\nВот так выглядит твоя анкета:\n\nAnon Shymkent🍁\n\n• {data['description']}\n\nИсточник - {data['status']}\n--------\nСтатус - ожидает одобрения⏳', reply_markup=result)

        await state.clear()

        btns = InlineKeyboardBuilder()
        btns.add(InlineKeyboardButton(text='Посмотреть анонимки', callback_data='moder_posts'))
        result = btns.as_markup()
        admins = await orm_get_admins(session)
        for data in admins:
            await bot.send_message(chat_id=data.tg_id, text='➕ Новая анонимка!', reply_markup=result)

    except KeyError:
        await callback.answer(f'Выберите статус!')

#! Конец FSM







