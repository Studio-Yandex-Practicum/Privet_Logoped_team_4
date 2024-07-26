import asyncio

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models import (Link, PromoCode, Role, SocialNetworkType, User,
                    async_session)


async def add_data(session):
    parent_role = Role(role_name='Parent')
    therapist_role = Role(role_name='Speech Therapist')
    session.add_all([parent_role, therapist_role])

    user1 = User(
        username='Parent1', fullname='John Dou',
        role=parent_role, social_network=SocialNetworkType.TG
    )
    user2 = User(
        username='Parent2', fullname='Alice Black',
        role=parent_role, social_network=SocialNetworkType.VK
    )
    user3 = User(
        username='Therapist1', fullname='Albert Mongo',
        role=therapist_role, social_network=SocialNetworkType.VK
    )
    session.add_all([user1, user2, user3])

    some_link1 = Link(
        link='https://example.com/some_link1', link_name='some_link1'
    )
    some_link2 = Link(
        link='https://example.com/some_link2', link_name='some_link2'
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
    result = await session.execute(
        select(Role).options(selectinload(Role.users))
    )
    roles = result.scalars().all()
    for role in roles:
        print(f'Role: {role.role_name}')
        for user in role.users:
            print(
                f'  User: {user.username}, Fullname: {user.fullname}'
            )

    result = await session.execute(
        select(User).options(selectinload(User.role))
    )
    users = result.scalars().all()
    for user in users:
        print(
            f'User: {user.username}, Fullname: {user.fullname}'
        )
        print(
            f'User: {user.username}, Fullname: {user.fullname}, '
            f'Role: {user.role.role_name}, '
            f'SocialNetwork: {user.social_network.value}'
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

if __name__ == "__main__":
    asyncio.run(async_main())
