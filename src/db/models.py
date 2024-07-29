import enum

from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String, func
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.db.config import database_url
from src.db.constants import RoleName

Base = declarative_base()


class RoleType(enum.Enum):
    """Enum типов ролей пользователей."""
    PARENT = RoleName.PARENT
    SPEECH_THERAPIST = RoleName.SPEECH_THERAPIST


class TGUser(AsyncAttrs, Base):
    """Модель пользователя телеграм."""
    __tablename__ = 'tg_users'
    user_id = Column(Integer, primary_key=True)
    role = Column(Enum(RoleType), nullable=False)
    is_admin = Column(Numeric, default=0)
    created_at = Column(DateTime, default=func.now())


class VKUser(AsyncAttrs, Base):
    """Модель пользователя вконтакте."""
    __tablename__ = 'vk_users'
    user_id = Column(Integer, primary_key=True)
    role = Column(Enum(RoleType), nullable=False)
    is_admin = Column(Numeric, default=0)
    created_at = Column(DateTime, default=func.now())


class Link(AsyncAttrs, Base):
    """Модель ссылок на различные рабочие материалы."""
    __tablename__ = 'links'
    link_id = Column(Integer, primary_key=True)
    link = Column(String(250), unique=True, nullable=False)
    link_name = Column(String(100), nullable=False)
    to_role = Column(Enum(RoleType), nullable=False)


class PromoCode(AsyncAttrs, Base):
    """Модель промокодов для пользователей."""
    __tablename__ = 'promocodes'
    promocode_id = Column(Integer, primary_key=True)
    promocode = Column(String(100), unique=True, nullable=False)
    file_path = Column(String(100), nullable=False)


engine = create_async_engine(database_url, echo=False)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
