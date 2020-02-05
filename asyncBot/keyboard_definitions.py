# class ButtonsSample:
#
#     def __init__(self, title, prefix, *parts):
#         self._title = title
#         self._prefix = prefix
#         self._parts = parts
#
# main_menu = (ButtonsSample('Премии 💵', 'main', 'award'))

from aiogram.utils.callback_data import CallbackData

menu_calldata = CallbackData('menu', 'name', 'goto')
