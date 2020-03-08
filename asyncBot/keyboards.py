from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

import emoji


class InlineKB(InlineKeyboardMarkup):

    PRESET = {
        'main_menu': [('Премии 💵', 'award'), ('Reminders ⌚', 'remind'), ('Задания 📖', 'task'),
                      ('Темы дня ☀', 'topics'), ('Трениги 🏋', 'training'), ('Штрафы 🤬', 'fine')],
        'admin_menu': [('Добавить ➕', 'add'), ('Изменить 🖊', 'edit'), ('Вещать 📯', 'broadcast')],
        'done_or_not': [('Сделал ✔', 'yes'), ('Не сделал ❌', 'no'), ('<-- Назад', 'back_to_main_menu')]
    }

    def __init__(self, preset=None, row_width=3, inline_keyboard=None, **kwargs):
        """

        Args:
            preset: Title of keyboard preset possible presets: main_menu

        """
        super().__init__(row_width, inline_keyboard, **kwargs)
        self._preset = preset

        self._buttons = []

    def generate_kb(self):

        for button_data in self.PRESET[self._preset]:
            button_tittle, callback_data = button_data[0], button_data[1]
            self._buttons.append(InlineKeyboardButton(button_tittle, callback_data=callback_data))

        self.add(*self._buttons)

        return self

    def if_name_suit_btn(self, user_name):
        self.add(InlineKeyboardButton('Хорошо👌', callback_data=f'{user_name}'))
        return self

    def admin_add(self):  # TODO Сделать одну функцию

        for button_data in self.PRESET['main_menu']:
            button_tittle, callback_data = button_data[0], button_data[1]
            self._buttons.append(InlineKeyboardButton(button_tittle, callback_data=f'add_{callback_data}'))

        self.add(*self._buttons)

        return self

    def admin_edit(self):

        for button_data in self.PRESET['main_menu']:
            button_tittle, callback_data = button_data[0], button_data[1]
            self._buttons.append(InlineKeyboardButton(button_tittle, callback_data=f'edit_{callback_data}'))

        self.add(*self._buttons)

        return self


    def get_user_buttons(self, users):

        for user in users:
            self._buttons.append(InlineKeyboardButton(user.name, callback_data=f'user_{user.user_id}'))

        self.add(*self._buttons)

        return self

    def pointers_buttons(self, pointers):

        for num, point in enumerate(pointers):
            self._buttons.append(InlineKeyboardButton(str(num + 1), callback_data=f'{point.type}_{point.id}'))

        self.add(*self._buttons)
        self.row(InlineKeyboardButton('<-- Назад', callback_data='back_to_main_menu'))
        return self
