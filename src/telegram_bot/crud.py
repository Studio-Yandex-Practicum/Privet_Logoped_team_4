import os
import sys

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.append(parent_folder_path)

from db.models import PromoCode, RoleType, TGUser, async_session # noqa


async def chose_role(user_id, role_type):
    """Добавление пользователя и смена роли."""
    if role_type == 'parent':
        role=RoleType.PARENT
    else:
        role=RoleType.SPEECH_THERAPIST
    async with async_session() as session:
        new_user = insert(TGUser).values(user_id=user_id, role=role).on_conflict_do_update(
            constraint=TGUser.__table__.primary_key,
            set_={TGUser.role: role}
        )
        await session.execute(new_user)
        await session.commit()


async def get_promocode(promo):
    """Получение пути файла промокода."""
    async with async_session() as session:
        result = await session.execute(
            select(PromoCode.file_path).where(PromoCode.promocode == promo)
        )
        promocode_file_path = result.scalars().first()
        return promocode_file_path


async def get_admin_users():
    """Получение id всех админов."""
    async with async_session() as session:
        result = await session.execute(
            select(TGUser.user_id).where(TGUser.is_admin == 1)
        )
        admins_id = result.scalars().all()
        return admins_id


async def get_user(user_id):
    async with async_session() as session:
        result = await session.execute(
            select(TGUser).where(TGUser.user_id == user_id)
        )
        user = result.scalars().first()
        return user


async def send_notification(bot, user_id, first_name, role_type):
    user = await get_user(user_id)
    admin_ids = await get_admin_users()
    print(f'{user = }')
    for admin in admin_ids:
        text = f'Зарегестрирован:{first_name} с ролью {role_type}'
        return await bot.send_message(chat_id=admin, text=text)
    # if user:
    #     for admin in admin_ids:
    #         text = f'Зарегестрирован:{first_name} с ролью {role_type}'
    #         return await bot.send_message(chat_id=admin, text=text)
