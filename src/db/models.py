import enum

from sqlalchemy import Column, DateTime, Enum, Integer, Numeric, String, func, BigInteger, Boolean
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import database_url
from .constants import LinkResourseType, RoleName

Base = declarative_base()


class RoleType(enum.Enum):
    """Enum типов ролей пользователей."""
    PARENT = RoleName.PARENT
    SPEECH_THERAPIST = RoleName.SPEECH_THERAPIST


class LinkType(enum.Enum):
    """Enum типов ссылок на ресурсы."""
    URL = LinkResourseType.URL
    FILEPATH = LinkResourseType.FILEPATH


class TGUser(AsyncAttrs, Base):
    """Модель пользователя телеграм."""
    __tablename__ = 'tg_users'
    user_id = Column(BigInteger, primary_key=True)
    role = Column(Enum(RoleType), nullable=False)
    is_admin = Column(Numeric, default=0)
    created_at = Column(DateTime, default=func.now())
    notificate_at = Column(Integer)
    notification_interval = Column(String(100))
    notification_day = Column(String(100))
    notification_access = Column(Boolean, default=False)


class VKUser(AsyncAttrs, Base):
    """Модель пользователя вконтакте."""
    __tablename__ = 'vk_users'
    user_id = Column(BigInteger, primary_key=True)
    role = Column(Enum(RoleType), nullable=False)
    is_admin = Column(Numeric, default=0)
    created_at = Column(DateTime, default=func.now())


class Link(AsyncAttrs, Base):
    """Модель ссылок на различные рабочие материалы."""
    __tablename__ = 'links'
    link_id = Column(Integer, primary_key=True)
    link = Column(String(250), unique=True, nullable=False)
    link_name = Column(String(100), nullable=False)
    link_type = Column(Enum(LinkType), nullable=False)
    to_role = Column(Enum(RoleType))


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
