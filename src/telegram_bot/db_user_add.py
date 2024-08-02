import os
import sys

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_folder_path)

from db.models import RoleType, PromoCode, TGUser, async_session


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
    """Получение промокода и его пути."""
    async with async_session() as session:
        result = await session.execute(
            select(PromoCode.file_path).where(PromoCode.promocode == promo)
        )
        promocode_user = result.scalars().first()
        return promocode_user
