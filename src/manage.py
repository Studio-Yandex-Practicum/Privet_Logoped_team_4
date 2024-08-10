import argparse
import asyncio

import aiohttp
from environs import Env

env = Env()
env.read_env()

api_url = env("API_EXT_URL")


async def promote_to_admin(user_id, platform):
    """Добавляет пользователя, как администратора для указанной платформы."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{api_url}/admins/',
            json={"user_id": user_id, "platform": platform}
                ) as response:
            if response.status == 200:
                print(
                    f'Пользователь с ID {user_id} на платформе '
                    f'{platform} назначен администратором.'
                )
            else:
                error_detail = await response.text()
                print(
                    'Ошибка добавления администратора: '
                    f'{response.status} - {error_detail}'
                )


async def demote_admin(user_id, platform):
    """Снимает у пользователя статус администратора для указанной платформы."""
    async with aiohttp.ClientSession() as session:
        async with session.patch(
            f'{api_url}/admins/',
            json={"user_id": user_id, "platform": platform}
                ) as response:
            if response.status == 200:
                print(
                    f'У пользователя с ID {user_id} на платформе '
                    f'{platform} снят статус администратора.'
                )
            else:
                error_detail = await response.text()
                print(
                    'Ошибка удаления администратора: '
                    f'{response.status} - {error_detail}'
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
