import os
import sys
from typing import Optional

from aiogram.filters.callback_data import CallbackData

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from db.models import NotificationIntervalType  # noqa
from db.models import ButtonType, NotificationWeekDayType, RoleType


class PromocodeDeleteCallback(CallbackData, prefix="promo_list_delete"):
    page: int = 0


class PromocodeItemDeleteCallback(CallbackData, prefix="delete_promo"):
    promocode_id: int


class ButtonInfoCallback(CallbackData, prefix="button_info"):
    button_id: int


class ButtonDeleteCallback(CallbackData, prefix="delete_button"):
    button_id: int


class ButtonTextCallback(CallbackData, prefix="text_button"):
    button_id: int


class ButtonOnButtonTextCallback(CallbackData, prefix="on_button_text"):
    button_id: int


class ButtonInMainMenuCallback(CallbackData, prefix="in_main_menu"):
    button_id: int
    is_enabled: bool


class ButtonTypeCallback(CallbackData, prefix="button_type"):
    button_id: int
    button_type: Optional[ButtonType] = None


class ButtonChooseRoleCallback(CallbackData, prefix="button_choose_role"):
    button_id: int


class ButtonRoleCallback(CallbackData, prefix="button_role"):
    button_id: int
    button_role: Optional[RoleType] = None


class ButtonGroupCallback(CallbackData, prefix="button_group"):
    button_id: Optional[int]


class ButtonAddCallback(CallbackData, prefix="button_add"):
    parent_button_id: Optional[int]


class ButtonAddTypeCallback(CallbackData, prefix="button_add2"):
    parent_button_id: Optional[int]
    button_type: ButtonType


class ButtonAddFileCallback(CallbackData, prefix="button_file"):
    button_id: int


class VisitButtonCallback(CallbackData, prefix="visit_button"):
    button_id: int
    authorized: bool = True


class SubscribeButtonCallback(CallbackData, prefix="subscribe_button"):
    button_id: int
    is_subscribed: bool


class MailingButtonSettings(CallbackData, prefix="mailing_settings"):
    role: Optional[RoleType]
    ignore_subscribed: bool


class MailingButtonRole(CallbackData, prefix="mailing_role"):
    role: Optional[RoleType]


class EnableNotifications(CallbackData, prefix="notify"):
    is_enabled: bool
    button_id: int


class NotificationIntervalCallback(CallbackData, prefix="notify_interval"):
    interval: Optional[NotificationIntervalType]
    button_id: int
    day_of_week: Optional[NotificationWeekDayType] = None
