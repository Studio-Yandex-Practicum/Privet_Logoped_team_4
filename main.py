import asyncio

from sqlalchemy import text

from models import Link, PromoCode, Role, SocialNetwork, User, async_session


async def add_data(session):
    # Добавление ролей
    parent_role = Role(role_name='Parent')
    therapist_role = Role(role_name='Speech Therapist')
    session.add_all([parent_role, therapist_role])

    # Добавление социальных сетей
    telegram_social_network = SocialNetwork(
        social_network_name='Telegram'
    )
    vk_social_network = SocialNetwork(social_network_name='VK')
    session.add_all([telegram_social_network, vk_social_network])

    # Добавление пользователей
    user1 = User(
        username='Parent1', fullname='John Dou',
        role=parent_role, social_network=telegram_social_network
    )
    user2 = User(
        username='Parent2', fullname='Alice Black',
        role=parent_role, social_network=vk_social_network
    )
    user3 = User(
        username='Therapist1', fullname='Albert Mongo',
        role=therapist_role, social_network=vk_social_network
    )
    session.add_all([user1, user2, user3])

    # Добавление ссылок
    some_link1 = Link(
        link='https://example.com/some_link1', link_name='some_link1'
    )
    some_link2 = Link(
        link='https://example.com/some_link2', link_name='some_link2'
    )
    session.add_all([some_link1, some_link2])

    # Добавление промокодов
    promocode1 = PromoCode(
        promocode='promo1', file_path='/home/promocodes/1'
    )
    promocode2 = PromoCode(
        promocode='promo2', file_path='/home/promocodes/2'
    )
    session.add_all([promocode1, promocode2])
    await session.commit()


async def fetch_data(session):
    # Получение всех ролей и их пользователей
    roles = await session.execute(text('SELECT * FROM roles'))
    for role in roles:
        print(f'Role: {role.role_name}')
        # for user in role.users:
        #     print(
        #         f'  User: {user.username}, Fullname: {user.fullname}'
        #     )

    # Получение всех ролей и их пользователей
    social_networks = await session.execute(
        text('SELECT * FROM social_networks')
    )
    for social_network in social_networks:
        print(f'SocialNetwork: {social_network.social_network_name}')
        # for user in social_network.users:
        #     print(
        #         f'  User: {user.username}, Fullname: {user.fullname}'
        #     )

    # Получение всех пользователей, их ролей и соц.сетей
    users = await session.execute(text('SELECT * FROM users'))
    for user in users:
        print(
            f'User: {user.username}, Fullname: {user.fullname}'
        )
        # print(
        #     f'User: {user.username}, Fullname: {user.fullname}, '
        #     f'Role: {user.role.role_name}, '
        #     f'SocialNetwork: {user.social_network.social_network_name}'
        # )

    # Получение всех ссылок
    links = await session.execute(text('SELECT * FROM links'))
    for link in links:
        print(f'Link: {link.link}, Link Name: {link.link_name}')

    # Получение всех ссылок
    promocodes = await session.execute(text('SELECT * FROM promocodes'))
    for promocode in promocodes:
        print(
            f'PromoCode: {promocode.promocode}, '
            f'File Path: {promocode.file_path}'
        )


async def async_main():
    async with async_session() as session:
        # await add_data(session)
        await fetch_data(session)

if __name__ == "__main__":
    asyncio.run(async_main())
