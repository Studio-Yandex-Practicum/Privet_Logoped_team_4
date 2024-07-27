import enum

from sqlalchemy import (Column, DateTime, Enum, ForeignKey, Integer, String,
                        func)
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from src.db.config import settings
from src.db.constants import SocialNetworkName

Base = declarative_base()


class Role(AsyncAttrs, Base):
    """Модель ролей пользователей."""
    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)

    users = relationship('User', back_populates='role')
    links = relationship('Link', back_populates='role')


class SocialNetworkType(enum.Enum):
    """Enum типов социальный сетей пользователей."""
    TG = SocialNetworkName.TELEGRAM
    VK = SocialNetworkName.VK


class User(AsyncAttrs, Base):
    """Модель пользователей."""
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    fullname = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.role_id'))
    social_network = Column(
        Enum(SocialNetworkType), nullable=False
    )
    created_at = Column(DateTime, default=func.now())

    role = relationship('Role', back_populates='users')


class Link(AsyncAttrs, Base):
    """Модель ссылок на различные рабочие материалы."""
    __tablename__ = 'links'
    link_id = Column(Integer, primary_key=True)
    link = Column(String(250), unique=True, nullable=False)
    link_name = Column(String(100), nullable=False)
    to_role_id = Column(Integer, ForeignKey('roles.role_id'))

    role = relationship('Role', back_populates='links')


class PromoCode(AsyncAttrs, Base):
    """Модель промокодов для пользователей."""
    __tablename__ = 'promocodes'
    promocode_id = Column(Integer, primary_key=True)
    promocode = Column(String(100), unique=True, nullable=False)
    file_path = Column(String(100), nullable=False)


engine = create_async_engine(settings.database_url, echo=False)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
