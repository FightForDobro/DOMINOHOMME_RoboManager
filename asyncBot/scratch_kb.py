from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from keyboard_definitions import menu_calldata

import emoji


class InlineMarkup(InlineKeyboardMarkup):
    PRESET = {
        'main_menu': {'calldata_sample': CallbackData('menu', 'goto'),
                      'parts': {'Премии 💵': {'goto': 'award'},
                                'Задания 📖': {'goto': 'task'},
                                'Штрафы 🤬': {'goto': 'fine'},
                                'Сообщения✉️': {'goto': 'message'}}
                      },

        'admin_menu': {'calldata_sample': CallbackData('admin', 'goto'),
                       'parts': {'Добавить ➕': {'goto': 'add'},
                                 'Изменить 🖊': {'goto': 'edit'},
                                 'Вещать 📯': {'goto': 'broadcast'}
                                 }},

        'done_or_not': {'calldata_sample': CallbackData('point', 'id', 'result'),
                        'parts': {'Сделал ✔': {},
                                  'Не сделал ❌': {}
                                  }},

        'sample': {'calldata_sample': CallbackData('admin', 'goto'),
                   'titles': {},
                   }
    }

    def __init__(self, preset=None, titles=None, parts=None, calldata_sample=None,
                 row_width=3, inline_keyboard=None, **kwargs):

        super().__init__(row_width=row_width, inline_keyboard=inline_keyboard, **kwargs)

        if preset:

            self._calldata_sample = self.PRESET[preset]['calldata_sample']
            self._titles = self.PRESET[preset]['parts'].keys()
            self._parts = self.PRESET[preset]['parts'].values()

        elif not preset:

            self._titles = titles
            self._parts = parts
            self._calldata_sample = calldata_sample

        else:
            # Добавить логи почему и как сюда могла попасть программа
            pass

    def generate_kb(self, parts: dict = None):
        """

        Args:
            parts(dict): Dictionary of key: value elements for callback factory

        Returns: InlineKeyboardMarkup

        """
        if parts:
            self._parts = parts

        for title, part in self._titles, self._parts:
            self.insert(InlineKeyboardButton(title, callback_data=self._calldata_sample.new(**self._parts)))

        return self

