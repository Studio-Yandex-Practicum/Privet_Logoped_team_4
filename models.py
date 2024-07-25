import os

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

Base = declarative_base()


class Role(AsyncAttrs, Base):
    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)

    users = relationship('User', back_populates='role')


class SocialNetwork(AsyncAttrs, Base):
    __tablename__ = 'social_networks'
    social_network_id = Column(Integer, primary_key=True)
    social_network_name = Column(String(50), unique=True, nullable=False)

    users = relationship('User', back_populates='social_network')


# Определяем модель
class User(AsyncAttrs, Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    fullname = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.role_id'))
    social_network_id = Column(
        Integer, ForeignKey('social_networks.social_network_id')
    )
    created_at = Column(DateTime, default=func.now())

    role = relationship('Role', back_populates='users')
    social_network = relationship('SocialNetwork', back_populates='users')


class Link(AsyncAttrs, Base):
    __tablename__ = 'links'
    link_id = Column(Integer, primary_key=True)
    link = Column(String(250), unique=True, nullable=False)
    link_name = Column(String(100), nullable=False)


class PromoCode(AsyncAttrs, Base):
    __tablename__ = 'promocodes'
    promocode_id = Column(Integer, primary_key=True)
    promocode = Column(String(100), unique=True, nullable=False)
    file_path = Column(String(100), nullable=False)


engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
