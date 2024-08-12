import logging

from config import api, labeler, state_dispenser
from handlers import (
    # add_link,
    add_promocode,
    # admin_links_handler,
    admin_promocodes_handler,
    admin_start_handler,
    # admin_upload_file_handler,
    # delete_link_handler,
    delete_promocode_handler,
    faq_handler,
    # get_link,
    # get_link_name,
    # get_link_type,
    get_promocode,
    parent_handler,
    role_handler,
    speech_therapist_handler,
    start_handler,
    admin_buttons_handler,
)
from vkbottle import BaseStateGroup, GroupEventType, DocMessagesUploader
from vkbottle.bot import Bot, Message, MessageEvent
from rules import PayloadRule
from keyboards.keyboards import cancel_keyboard

logging.basicConfig(level=logging.INFO)

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)
bot.labeler.vbml_ignore_case = True
doc_uploader = DocMessagesUploader(bot.api)


class UserStates(BaseStateGroup):
    """Стейты пользователя."""

    ROLE_STATE = "choose_role"
    PARENT_STATE = "parent_options"
    FAQ_STATE = "faq_options"
    SPEECH_THERAPIST_STATE = "speech_therapist_options"


class AdminStates(BaseStateGroup):
    """Стейты администратора."""

    ADMIN_STATE = "admin_options"
    LINKS_STATE = "links_options"
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


@bot.on.private_message(lev="/admin")
async def admin_start(message: Message):
    await admin_start_handler(bot, message, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "button_info"}),
)
async def admin_button(event: MessageEvent):
    await admin_buttons_handler.button_info_handler(bot, event)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_text"}),
)
async def admin_button_text(event: MessageEvent):
    await admin_buttons_handler.button_on_text_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_file"}),
)
async def admin_button_edit_file(event: MessageEvent):
    await admin_buttons_handler.button_add_file_callback(
        bot, event, AdminStates
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "delete_button"}),
)
async def admin_button_delete(event: MessageEvent):
    await admin_buttons_handler.button_delete_handler(bot, event)


@bot.on.private_message(state=AdminStates.WAITING_ON_BUTTON_TEXT)
async def admin_options_on_button_text(message: Message):
    await admin_buttons_handler.get_button_on_text(bot, message)


@bot.on.private_message(state=AdminStates.WAITING_BUTTON_FILE)
async def admin_options_on_button_file(message: Message):
    await admin_buttons_handler.get_button_file_edit(message, AdminStates, bot)


@bot.on.private_message(state=AdminStates.WAITING_BUTTON_FILE_CREATE)
async def admin_options_on_button_file_create(message: Message):
    await admin_buttons_handler.get_button_file_create(
        message, AdminStates, bot
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_click_text"}),
)
async def admin_button_edit_click_text(event: MessageEvent):
    await admin_buttons_handler.button_text_handler(bot, event, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_BUTTON_TEXT)
async def admin_options_waiting_button_text(message: Message):
    await admin_buttons_handler.get_button_text(bot, AdminStates, message)


@bot.on.private_message(state=AdminStates.WAITING_BUTTON_TEXT_CREATE)
async def admin_options_waiting_button_text_create(message: Message):
    await admin_buttons_handler.get_button_text_create(
        message, AdminStates, bot
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_roles"}),
)
async def admin_button_edit_role(event: MessageEvent):
    await admin_buttons_handler.button_choose_role_handler(
        bot, event, AdminStates
    )


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "button_role"}),
)
async def admin_button_role(event: MessageEvent):
    await admin_buttons_handler.button_role_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "edit_group"}),
)
async def admin_edit_group(event: MessageEvent):
    await admin_buttons_handler.admin_buttons_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "buttons"}),
)
async def admin_button_list(event: MessageEvent):
    await admin_buttons_handler.admin_buttons_handler(bot, event, AdminStates)


@bot.on.raw_event(
    GroupEventType.MESSAGE_EVENT,
    MessageEvent,
    PayloadRule({"type": "button_click"}),
)
async def button_click(event: MessageEvent):
    await admin_buttons_handler.button_click_handler(bot, event, doc_uploader)


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
)
async def admin_button_add(event: MessageEvent):
    if "button_type" in event.object.payload:
        await admin_buttons_handler.button_add_type_handler(
            bot, event, AdminStates
        )
    else:
        await admin_buttons_handler.button_add_handler(bot, event, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_ON_BUTTON_TEXT_CREATE)
async def admin_options_on_button_text_create(message: Message):
    await admin_buttons_handler.get_on_button_text_create(
        message, AdminStates, bot
    )


# @bot.on.private_message(state=AdminStates.ADMIN_STATE)
# async def admin_options(message: Message):
#     await admin_handler(bot, message, AdminStates)


# @bot.on.private_message(state=AdminStates.LINKS_STATE)
# async def links_options(message: Message):
#     await admin_links_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_LINK)
async def waiting_link(message: Message):
    await get_link(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_LINK_NAME)
async def waiting_link_name(message: Message):
    await get_link_name(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_LINK_TYPE)
async def waiting_link_type(message: Message):
    await get_link_type(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_LINK_TO_ROLE)
async def waiting_to_role(message: Message):
    await add_link(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.DELETE_LINK)
async def delete_link(message: Message):
    await delete_link_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.PROMOCODES_STATE)
async def promocodes_options(message: Message):
    await admin_promocodes_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_PROMOCODE)
async def waiting_promocode(message: Message):
    await get_promocode(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_PROMOCODE_FILEPATH)
async def waiting_promocode_filepath(message: Message):
    await add_promocode(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.DELETE_PROMOCODE)
async def delete_promocode(message: Message):
    await delete_promocode_handler(bot, message, AdminStates)


@bot.on.private_message(
    state=[AdminStates.UPLOAD_LINK_FILE, AdminStates.UPLOAD_PROMOCODE_FILE]
)
async def upload_file(message: Message):
    await admin_upload_file_handler(bot, message, AdminStates)


@bot.on.private_message(lev=["/start", "Начать"])
async def greeting(message: Message):
    await start_handler(bot, message, UserStates)


@bot.on.private_message(lev=["/promo", "Промокод"])
async def promo(message: Message):
    await message.answer("Введите промокод:", keyboard=cancel_keyboard)
    await bot.state_dispenser.set(message.peer_id, UserStates.PROMOCODE_STATE)


@bot.on.private_message(state=UserStates.ROLE_STATE)
async def choose_role(message: Message):
    await role_handler(bot, message, UserStates)


@bot.on.private_message(state=UserStates.PARENT_STATE)
async def parent_options(message: Message):
    await parent_handler(bot, message, UserStates)


@bot.on.private_message(state=UserStates.FAQ_STATE)
async def faq_options(message: Message):
    await faq_handler(bot, message, UserStates)


@bot.on.private_message(state=UserStates.SPEECH_THERAPIST_STATE)
async def speech_therapist_options(message: Message):
    await speech_therapist_handler(bot, message, UserStates)


if __name__ == "__main__":
    bot.run_forever()
