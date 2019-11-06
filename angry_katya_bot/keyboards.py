from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


class InlineKB(InlineKeyboardMarkup):

    def __init__(self, row_width=3):
        super().__init__(row_width=row_width)

    def generate_kb(self, *args, **kwargs):
        """
        :param args: Buttons names
        :param kwargs: Buttons names with specific callback data key is callback_data value is button name
        """

        buttons = [InlineKeyboardButton(b, callback_data=b) for b in args]

        if kwargs:
            k_buttons = [InlineKeyboardButton(b, callback_data=d) for d, b in kwargs.items()]
            self.add(*buttons + k_buttons)
            return self

        self.add(*buttons)
        return self
