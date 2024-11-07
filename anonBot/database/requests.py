import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Post, User, Channels


#Регистрация юзера
async def orm_registartion(session: AsyncSession, data: dict):
    obj = User(
        tg_id=data["tg_id"],
        tag=data["tag"],
        premium_status=data["premium_status"],
        admin_status=data["admin_status"],
        moder_status=data["moder_status"],
        stars=data["stars"],
        count_all_posts=data['count_all_posts'],
    )
    session.add(obj)
    await session.commit()

#Проверка зарегистрирован ли юзер
async def orm_check_registration(session: AsyncSession, user_id: int):
    query = select(User).where(User.tg_id == user_id)
    result = await session.execute(query)
    #await session.commit()
    return result.scalar()


#Добавление поста в БД
async def orm_add_post(session: AsyncSession, data: dict):
    date = datetime.datetime.now()
    obj = Post(
        description=data["description"],
        tg_id=data["tg_id"],
        tg_tag=data["tg_tag"],
        premium=data["premium"],
        photo=data['photo'],
        status=data["status"],
        date=date.date()
    )
    session.add(obj)
    await session.commit()


#Добавление канала для обязательных подписок
async def orm_add_channel(session: AsyncSession, data: dict):
    obj = Channels(
        channel_name=data["channel_name"],
        url=data["url"],
        owner_id=data["owner_id"],
        limit=data["limit"]
    )
    session.add(obj)
    await session.commit()


async def orm_get_channels(session: AsyncSession):
    query = select(Channels)
    result = await session.execute(query)
    return result.scalars().all()
        

async def orm_delete_channel(session: AsyncSession,  ids: int):
    query = delete(Channels).where(Channels.id == ids)
    result = await session.execute(query)
    await session.commit()

async def orm_get_post(session: AsyncSession):
    query = select(Post)

    result = await session.execute(query)

    return result.scalars().all()


async def orm_get_post_to_publich(session: AsyncSession, post_id: int):
    query = select(Post).where(Post.id == post_id)

    result = await session.execute(query)

    return result.scalar()

async def orm_delete_post(session: AsyncSession, post_id: int):
    query = delete(Post).where(Post.id == post_id)

    result = await session.execute(query)
    
    await session.commit()



async def orm_info_post(session: AsyncSession, id: int):
    query = select(Post).where(Post.id == id)

    result = await session.execute(query)

    return result.scalars().all()

async def orm_get_count_posts(session: AsyncSession, id: int):
    query = select(User).where(User.tg_id == id)

    result = await session.execute(query)

    return result.scalar()



async def orm_add_count_post(session: AsyncSession, id: int, data: int):
    query = update(User).where(User.tg_id == id).values(count_all_posts=data)
    await session.execute(query)
    await session.commit()

async def orm_edit_post(session: AsyncSession, post_id: int, data: str):
    query = update(Post).where(Post.id == post_id).values(description=data)
    await session.execute(query)
    await session.commit()



async def orm_get_posts(session: AsyncSession, user_id: int):
    query = select(Post).where(Post.tg_id == user_id)

    result = await session.execute(query)

    return result.scalars().all()
  
async def orm_get_all_users(session: AsyncSession):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return len(users)

async def orm_get_all_posts(session: AsyncSession):
    result = await session.execute(select(Post))
    posts = result.scalars().all()
    return len(posts)

async def orm_get_all_user_ids(session: AsyncSession):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users

async def orm_delete_user(session: AsyncSession, user_id: int):
    query = delete(User).where(User.tg_id == user_id)
    await session.execute(query)
    await session.commit()

async def orm_get(session: AsyncSession, user_id: int):
    query = update(User).where(User.tg_id == user_id).values(admin_status=True)

    await session.execute(query)
    await session.commit()

async def orm_get_admins(session: AsyncSession):
    query = select(User).where(User.admin_status == True)

    result = await session.execute(query)

    return result.scalars()


