from sqlalchemy import select
from db.models import async_session, PromoCode


async def get_promocode(promo):
    """Получение пути файла промокода."""
    async with async_session() as session:
        result = await session.execute(
            select(PromoCode.file_path).where(PromoCode.promocode == promo)
        )
        promocode_file_path = result.scalars().first()
        return promocode_file_path
