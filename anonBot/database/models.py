from sqlalchemy import TEXT, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(primary_key=False, nullable=False)
    tag: Mapped[str] = mapped_column(String(50), nullable=False)
    premium_status: Mapped[bool] = mapped_column(nullable=False) 
    moder_status: Mapped[bool] = mapped_column(nullable=False)
    admin_status: Mapped[bool] = mapped_column(nullable=False)
    stars: Mapped[int] = mapped_column(primary_key=False, nullable=False)
    count_all_posts: Mapped[int] = mapped_column(nullable=False)


class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(TEXT)
    photo: Mapped[str] = mapped_column(TEXT)
    tg_id: Mapped[int] = mapped_column()
    tg_tag: Mapped[str] = mapped_column(String(50))
    premium: Mapped[bool] = mapped_column()
    status: Mapped[str] = mapped_column(String(5))
    date: Mapped[str] = mapped_column(String(20))


class Channels(Base):
    __tablename__ = 'channel'

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_name: Mapped[str] = mapped_column(String(96), nullable=False)
    url: Mapped[str] = mapped_column(String(32), nullable=False)
    owner_id: Mapped[int] = mapped_column(nullable=False)
    limit: Mapped[int] = mapped_column('100')





