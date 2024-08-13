from aiogram.filters.callback_data import CallbackData
import sys
import os
from typing import Optional

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
from db.models import ButtonType, RoleType  # noqa


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
