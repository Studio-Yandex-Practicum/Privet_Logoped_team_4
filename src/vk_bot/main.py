from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import api, labeler, state_dispenser
from handlers import (
    admin_buttons_handler,
    admin_mailing_handler,
    admin_promocodes_handler,
    admin_start_handler,
    admin_start_handler_callback,
    admin_users_handler,
    ask_admin_handler,
    faq_handler,
    notification_handler,
    role_handler,
    start_handler,
)
from keyboards.keyboards import cancel_keyboard
from middleware import BanMiddleware
from notifications import every_day_notification, other_day_notification
from rules import PayloadRule
from vkbottle import BaseStateGroup, DocMessagesUploader, GroupEventType
from vkbottle.bot import Bot, Message, MessageEvent
from rules import AdminRule

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)
bot.labeler.vbml_ignore_case = True
doc_uploader = DocMessagesUploader(bot.api)

bot.labeler.message_view.register_middleware(BanMiddleware)


class UserStates(BaseStateGroup):
    """Стейты пользователя."""

    ROLE_STATE = "choose_role"
    PARENT_STATE = "parent_options"
    FAQ_STATE = "faq_options"
    SPEECH_THERAPIST_STATE = "speech_therapist_options"
    PROMOCODE_STATE = "enter_promocode"
    WAITING_FOR_MESSAGE = "waiting_for_message"
    NOTIFICATION_HOUR = "notification_hour"


class AdminStates(BaseStateGroup):
    """Стейты администратора."""

    ADMIN_STATE = "admin_options"
    LINKS_STATE = "links_options"
    USERS_STATE = "users_options"
    PROMOCODES_STATE = "promocodes_options"
    WAITING_LINK_NAME = "waiting_link_name"
    WAITING_LINK_TYPE = "waiting_link_type"
    WAITING_LINK = "waiting_link"
    WAITING_LINK_TO_ROLE = "waiting_link_to_role"
    DELETE_LINK = "delete_link"
    WAITING_PROMOCODE = "waiting_promocode"
    WAITING_PROMOCODE_FILEPATH = "waiting_promocode_filepath"
    DELETE_PROMOCODE = "delete_promocode"
    UPLOAD_LINK_FILE = "upload_link_file"
    UPLOAD_PROMOCODE_FILE = "upload_promocode_file"
    WAITING_BUTTON_FILE = "waiting_button_file"
    WAITING_ON_BUTTON_TEXT = "waiting_on_button_text"
    WAITING_BUTTON_TEXT = "waiting_button_text"
    WAITING_ON_BUTTON_TEXT_CREATE = "waiting_on_button_text_create"
    WAITING_BUTTON_TEXT_CREATE = "waiting_button_text_create"
    WAITING_BUTTON_FILE_CREATE = "waiting_button_file_create"
    WAITING_USER_ID_TO_BAN = "waiting_user_id_to_ban"
    WAITING_USER_ID_TO_UNBAN = "waiting_user_id_to_unban"
    SEND_MAILING = "send_mailing"
    MAILING_SETTINGS = "mailing_settings"


@bot.on.private_message(AdminRule(), lev="/admin")
async def admin_start(message: Message):
    await admin_start_handler(bot, message, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "main_info"}),
)
async def admin_main_info(event: MessageEvent):
    await admin_buttons_handler.main_menu_button_list(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "choose_role"}),
)
async def choose_role(event: MessageEvent):
    await start_handler.choose_role_handler(bot, event, UserStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "admin"}),
    AdminRule(),
)
async def admin(event: MessageEvent):
    await admin_start_handler_callback(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "button_info"}),
    AdminRule(),
)
async def admin_button(event: MessageEvent):
    await admin_buttons_handler.button_info_handler(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_text"}),
    AdminRule(),
)
async def admin_button_text(event: MessageEvent):
    await admin_buttons_handler.button_on_text_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_file"}),
    AdminRule(),
)
async def admin_button_edit_file(event: MessageEvent):
    await admin_buttons_handler.button_add_file_callback(
        bot, event, AdminStates
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "delete_button"}),
    AdminRule(),
)
async def admin_button_delete(event: MessageEvent):
    await admin_buttons_handler.button_delete_handler(bot, event)


@bot.on.private_message(AdminRule(), state=AdminStates.WAITING_ON_BUTTON_TEXT)
async def admin_options_on_button_text(message: Message):
    await admin_buttons_handler.get_button_on_text(bot, message)


@bot.on.private_message(AdminRule(), state=AdminStates.WAITING_BUTTON_FILE)
async def admin_options_on_button_file(message: Message):
    await admin_buttons_handler.get_button_file_edit(message, AdminStates, bot)


@bot.on.private_message(
    AdminRule(), state=AdminStates.WAITING_BUTTON_FILE_CREATE
)
async def admin_options_on_button_file_create(message: Message):
    await admin_buttons_handler.get_button_file_create(
        message, AdminStates, bot
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_click_text"}),
    AdminRule(),
)
async def admin_button_edit_click_text(event: MessageEvent):
    await admin_buttons_handler.button_text_handler(bot, event, AdminStates)


@bot.on.private_message(AdminRule(), state=AdminStates.WAITING_BUTTON_TEXT)
async def admin_options_waiting_button_text(message: Message):
    await admin_buttons_handler.get_button_text(bot, AdminStates, message)


@bot.on.private_message(
    AdminRule(), state=AdminStates.WAITING_BUTTON_TEXT_CREATE
)
async def admin_options_waiting_button_text_create(message: Message):
    await admin_buttons_handler.get_button_text_create(
        message, AdminStates, bot
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_roles"}),
    AdminRule(),
)
async def admin_button_edit_role(event: MessageEvent):
    await admin_buttons_handler.button_choose_role_handler(
        bot, event, AdminStates
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "button_role"}),
    AdminRule(),
)
async def admin_button_role(event: MessageEvent):
    await admin_buttons_handler.button_role_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_group"}),
    AdminRule(),
)
async def admin_edit_group(event: MessageEvent):
    await admin_buttons_handler.admin_buttons_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "buttons"}),
    AdminRule(),
)
async def admin_button_list(event: MessageEvent):
    await admin_buttons_handler.admin_buttons_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "button_click"}),
)
async def button_click(event: MessageEvent):
    await admin_buttons_handler.button_click_handler(
        bot, event, doc_uploader, UserStates
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "enable_notifications"}),
)
async def enable_notifications(event: MessageEvent):
    await notification_handler.enable_notifications(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "notification_interval"}),
)
async def notification_interval(event: MessageEvent):
    payload = event.object.payload
    if "day_of_week" in payload and payload["day_of_week"] is not None:
        await notification_handler.choose_day_of_week(bot, event, UserStates)
    elif "interval" in payload and payload["interval"] is not None:
        await notification_handler.choose_interval_select(
            bot, event, UserStates
        )
    else:
        await notification_handler.choose_interval(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "button_list"}),
)
async def button_list(event: MessageEvent):
    await admin_buttons_handler.button_list(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "button_add"}),
    AdminRule(),
)
async def admin_button_add(event: MessageEvent):
    if "button_type" in event.object.payload:
        await admin_buttons_handler.button_add_type_handler(
            bot, event, AdminStates
        )
    else:
        await admin_buttons_handler.button_add_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "show_in_main_menu"}),
    AdminRule(),
)
async def button_main_menu_admin(event: MessageEvent):
    await admin_buttons_handler.show_in_main_menu(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "role"}),
)
async def choose_role2(event: MessageEvent):
    await start_handler.role_handler(bot, event)


@bot.on.private_message(state=AdminStates.WAITING_ON_BUTTON_TEXT_CREATE)
async def admin_options_on_button_text_create(message: Message):
    await admin_buttons_handler.get_on_button_text_create(
        message, AdminStates, bot
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "promocodes"}),
    AdminRule(),
)
async def promocodes_admin(event: MessageEvent):
    await admin_promocodes_handler.promocodes_menu(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "add_promocode"}),
    AdminRule(),
)
async def add_promocodes_admin(event: MessageEvent):
    await admin_promocodes_handler.add_promocode(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "delete_promocode"}),
    AdminRule(),
)
async def delete_promocodes_admin(event: MessageEvent):
    await admin_promocodes_handler.delete_button_promocode_handler(
        bot, event, AdminStates
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "users"}),
    AdminRule(),
)
async def users_admin(event: MessageEvent):
    await admin_users_handler.admin_users_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "ban_user"}),
    AdminRule(),
)
async def ban_user_click(event: MessageEvent):
    await admin_users_handler.ban_user_click(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "unban_user"}),
    AdminRule(),
)
async def unban_user_click(event: MessageEvent):
    await admin_users_handler.unban_user_click(bot, event, AdminStates)


@bot.on.message(AdminRule(), state=AdminStates.DELETE_PROMOCODE)
async def delete_promocodes_admin_text(message: Message):
    await admin_promocodes_handler.delete_promocode_handler(
        bot, message, AdminStates
    )


@bot.on.message(AdminRule(), state=AdminStates.WAITING_PROMOCODE)
async def add_promocodes_admin_text(message: Message):
    await admin_promocodes_handler.add_promocode_text(
        bot, message, AdminStates
    )


@bot.on.message(AdminRule(), state=AdminStates.WAITING_PROMOCODE_FILEPATH)
async def add_promocodes_admin_filepath(message: Message):
    await admin_promocodes_handler.add_promocode_file(
        bot, message, AdminStates
    )


@bot.on.private_message(AdminRule(), state=AdminStates.USERS_STATE)
async def users_options(message: Message):
    await admin_users_handler(bot, message, AdminStates)


@bot.on.private_message(AdminRule(), state=AdminStates.WAITING_USER_ID_TO_BAN)
async def waiting_user_id_to_ban(message: Message):
    await admin_users_handler.ban_user(bot, message, AdminStates)


@bot.on.private_message(
    AdminRule(), state=AdminStates.WAITING_USER_ID_TO_UNBAN
)
async def waiting_user_id_to_unban(message: Message):
    await admin_users_handler.unban_user(bot, message, AdminStates)


@bot.on.private_message(lev=["/start", "Начать"])
async def greeting(message: Message):
    await start_handler.start_handler(bot, message, UserStates)


@bot.on.private_message(lev=["/role", "Сменить роль"])
async def cmd_role(message: Message):
    await start_handler.choose_role_cmd(bot, message)


@bot.on.private_message(lev=["/promo", "Промокод"])
async def promo(message: Message):
    await message.answer("Введите промокод:", keyboard=cancel_keyboard)
    await bot.state_dispenser.set(message.peer_id, UserStates.PROMOCODE_STATE)


@bot.on.private_message(state=UserStates.ROLE_STATE)
async def choose_role3(message: Message):
    await role_handler(message)


@bot.on.private_message(state=UserStates.NOTIFICATION_HOUR)
async def notification_hour(message: Message):
    await notification_handler.choose_interval_select_hour(bot, message)


@bot.on.private_message(state=UserStates.FAQ_STATE)
async def faq_options(message: Message):
    await faq_handler(bot, message, UserStates)


@bot.on.private_message(state=UserStates.PROMOCODE_STATE)
async def enter_promocode(message: Message):
    await start_handler.promocode_handler(bot, message, doc_uploader)


@bot.on.private_message(state=UserStates.WAITING_FOR_MESSAGE)
async def handle_user_message_state(message: Message):
    await ask_admin_handler.handle_user_message(bot, message, UserStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "mailing"}),
)
async def cmd_mailing(event: MessageEvent):
    await admin_mailing_handler.cmd_mailing(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "send_mailing"}),
)
async def send_mailing(event: MessageEvent):
    await admin_mailing_handler.send_mailing(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "mailing_settings"}),
)
async def mailing_settings(event: MessageEvent):
    await admin_mailing_handler.mailing_settings(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "mailing_settings_role"}),
)
async def mailing_settings_role(event: MessageEvent):
    await admin_mailing_handler.mailing_settings_role(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "mailing_role"}),
)
async def mailing_settings_role_select(event: MessageEvent):
    await admin_mailing_handler.mailing_settings_role_select(
        bot, event, AdminStates
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "send_mailing_messages"}),
)
async def send_mailing_messages(event: MessageEvent):
    await admin_mailing_handler.send_mailing_messages(bot, event, AdminStates)


@bot.on.private_message(state=AdminStates.SEND_MAILING)
async def send_mailing_state(message: Message):
    await admin_mailing_handler.mailing_message(bot, message, AdminStates)


@bot.on.private_message()
async def default(message: Message):
    await start_handler.promocode_handler(bot, message, doc_uploader, False)


if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        every_day_notification,
        CronTrigger.from_crontab("0 * * * *"),
        args=[bot],
    )
    scheduler.add_job(
        other_day_notification,
        CronTrigger.from_crontab("0 * */2 * *"),
        args=[bot],
    )
    scheduler.start()
    bot.run_forever()
