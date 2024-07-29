import asyncio

from models import (Link, PromoCode, RoleType, TGUser,
                    VKUser, async_session)
from sqlalchemy.future import select


async def add_data(session):
    """Проверка на вставку данных в базу данных."""
    user1 = TGUser(
        user_id=1, role=RoleType.PARENT
    )
    user2 = VKUser(
        user_id=2, role=RoleType.PARENT
    )
    user3 = VKUser(
        user_id=3, role=RoleType.SPEECH_THERAPIST
    )
    session.add_all([user1, user2, user3])

    some_link1 = Link(
        link='https://example.com/some_link1', link_name='some_link1',
        to_role=RoleType.PARENT
    )
    some_link2 = Link(
        link='https://example.com/some_link2', link_name='some_link2',
        to_role=RoleType.SPEECH_THERAPIST
    )
    session.add_all([some_link1, some_link2])

    promocode1 = PromoCode(
        promocode='promo1', file_path='/home/promocodes/1'
    )
    promocode2 = PromoCode(
        promocode='promo2', file_path='/home/promocodes/2'
    )
    session.add_all([promocode1, promocode2])
    await session.commit()


async def fetch_data(session):
    """Проверка на получение данных из базы данных."""
    result = await session.execute(
        select(TGUser)
    )
    users = result.scalars().all()
    for user in users:
        print(
            f'TGUser: {user.user_id}, '
            f'Role: {user.role}, '
            f'Created_at: {user.created_at}'
        )

    result = await session.execute(
        select(VKUser)
    )
    users = result.scalars().all()
    for user in users:
        print(
            f'VKUser: {user.user_id}, '
            f'Role: {user.role}, '
            f'Created_at: {user.created_at}'
        )

    result = await session.execute(select(Link))
    links = result.scalars().all()
    for link in links:
        print(f'Link: {link.link}, Link Name: {link.link_name}')

    result = await session.execute(select(PromoCode))
    promocodes = result.scalars().all()
    for promocode in promocodes:
        print(
            f'PromoCode: {promocode.promocode}, '
            f'File Path: {promocode.file_path}'
        )


async def async_main():
    async with async_session() as session:
        await add_data(session)
        await fetch_data(session)

if __name__ == '__main__':
    asyncio.run(async_main())
