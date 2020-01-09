from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
import db


class InlineKB(InlineKeyboardMarkup):

    DEFINITIONS = {'main_kb': ['Премии', 'Напоминания', 'Задания',
                               'Темы дня', 'Трениги', 'Штрафы'],

                   'admin_kb': ['Темы дня+', 'Дни рождения+', 'Премии+',
                                'Штрафы+', 'Задания+', 'Тренинги+',
                                'Напоминания+', 'Сообщения']}

    def __init__(self, row_width=3):
        super().__init__(row_width=row_width)

    def generate_kb(self, category=None, go_back=False, *args, **kwargs):
        """
        :param args: Buttons names
        :param kwargs: Buttons names with specific callback data key is callback_data value is button name
        :param category: Type of keyboard
        :param go_back: Add back button
        """

        if category is not None:
            args = self.DEFINITIONS[category]

        buttons = [InlineKeyboardButton(b, callback_data=b) for b in args]

        if kwargs:
            k_buttons = [InlineKeyboardButton(b, callback_data=d) for d, b in kwargs.items()]
            self.add(*buttons + k_buttons)

        else:
            self.add(*buttons)

        if go_back:
            self.go_back()

        return self

    def go_back(self):

        self.add(InlineKeyboardButton('<< Назад <<', callback_data='back'))
        return self

    def done_or_not(self, task_id):
        
        self.add(InlineKeyboardButton(f'\N{White Heavy Check Mark}', callback_data=f'done-{task_id}'),
                 InlineKeyboardButton(f'\N{Cross Mark}', callback_data=f'not_done-{task_id}'))
        self.add(InlineKeyboardButton('<< Назад <<', callback_data='back'))

        return self

    def message_kb(self):

        self.add(InlineKeyboardButton(f'>>>', callback_data=f'Сообщения'))

        return self

    def show_users(self, category):

        buttons = []

        for user in db.User.objects():
            buttons.append(InlineKeyboardButton(user.name, callback_data=f'add-{category}-{user.id}'))

        self.add(*buttons)
        return self
