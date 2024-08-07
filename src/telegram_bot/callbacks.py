from aiogram.filters.callback_data import CallbackData


class PromocodeDeleteCallback(CallbackData, prefix="promo_list_delete"):
    page: int = 0


class PromocodeItemDeleteCallback(CallbackData, prefix="delete_promo"):
    promocode_id: int
