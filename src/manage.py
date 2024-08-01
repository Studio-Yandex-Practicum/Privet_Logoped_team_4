import argparse
import asyncio

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from db.config import database_url
from db.models import RoleType, TGUser, VKUser

engine = create_async_engine(database_url, echo=False)


async def promote_to_admin(user_id, platform):
    """Добавляет пользователя, как администратора для указанной платформы."""
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    if platform == 'telegram':
        model = TGUser
    else:
        model = VKUser
    async with async_session() as session:
        async with session.begin():
            new_admin = insert(model).values(
                user_id=user_id, role=RoleType.SPEECH_THERAPIST, is_admin=1
                ).on_conflict_do_update(
                constraint=model.__table__.primary_key,
                set_={model.is_admin: 1}
            )
            await session.execute(new_admin)
            await session.commit()
        print(
            f'Пользователь с ID {user_id} на платформе '
            f'{platform} назначен администратором.'
        )


async def demote_admin(user_id, platform):
    """Снимает у пользователя статус администратора для указанной платформы."""
    async_session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    if platform == 'telegram':
        model = TGUser
    else:
        model = VKUser
    async with async_session() as session:
        async with session.begin():
            delete_admin = update(model).where(
                model.user_id == user_id
                ).values(is_admin=0)
            await session.execute(delete_admin)
            await session.commit()
        print(
            f'У пользователя с ID {user_id} на платформе '
            f'{platform} снят статус администратора.'
        )


async def main():
    """Командный интерфейс для добавления админов."""
    parser = argparse.ArgumentParser(
        description='Командный интерфейс для управления ботом'
    )
    subparsers = parser.add_subparsers(dest='command', help='Команды')

    admin_parser = subparsers.add_parser(
        'promote', help='Назначить пользователя администратором'
    )
    admin_parser.add_argument('user_id', type=int, help='ID пользователя')
    admin_parser.add_argument(
        'platform', choices=['telegram', 'vk'], help='Платформа пользователя'
    )

    not_admin_parser = subparsers.add_parser(
        'demote', help='Снять у пользователя статус администратора'
    )
    not_admin_parser.add_argument('user_id', type=int, help='ID пользователя')
    not_admin_parser.add_argument(
        'platform', choices=['telegram', 'vk'], help='Платформа пользователя'
    )

    args = parser.parse_args()

    if args.command == 'promote':
        await promote_to_admin(args.user_id, args.platform)
    elif args.command == 'demote':
        await demote_admin(args.user_id, args.platform)
    else:
        parser.print_help()


if __name__ == '__main__':
    asyncio.run(main())
