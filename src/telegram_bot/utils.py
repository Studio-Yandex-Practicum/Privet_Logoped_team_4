async def send_notification(user, bot):
    await bot.send_message(user.user_id, 'Вам пришло уведомление!')
