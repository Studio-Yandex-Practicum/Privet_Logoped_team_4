import aiohttp
from config import api_url


async def chose_role(user_id, role_type):
    """Добавление пользователя и смена роли."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{api_url}/tg_users/',
            json={"user_id": user_id, "role": role_type, "is_admin": 0}
                ) as response:
            return response


async def get_promocode(promo):
    """Получение пути файла промокода."""
    # async with async_session() as session:
    #     result = await session.execute(
    #         select(PromoCode.file_path).where(PromoCode.promocode == promo)
    #     )
    #     promocode_file_path = result.scalars().first()
    #     return promocode_file_path
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{api_url}/promocodes/{promo}'
                ) as response:
            if response.status == 200:
                promocode_data = await response.json()
                print('')
                print(f'promocode_data {promocode_data}')
                print('')
                return promocode_data
            else:
                return


async def get_admin_users():
    """Получение id всех админов."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{api_url}/tg_users/admins/{1}') as response:
            admins_ids = await response.json()
            print('')
            print(f'admins_ids {admins_ids}')
            print('')
        return admins_ids


async def get_user(user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{api_url}/tg_users/{user_id}'
                ) as response:
            tg_user_get_data = await response.json()
        return tg_user_get_data


async def send_notification(bot, user_id, first_name, role_type):
    # user = await get_user(user_id)
    admin_ids = await get_admin_users()
    for admin in admin_ids:
        text = f'Зарегистрирован:{first_name} с ролью {role_type}'
        return await bot.send_message(chat_id=admin, text=text)
