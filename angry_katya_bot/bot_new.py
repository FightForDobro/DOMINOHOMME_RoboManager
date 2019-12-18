import telebot
from keyboards import InlineKB

import db
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    """
    Стартовая функция запускает работу с ботом

    Последовательность работы:
    1. Проверяет ид чата
    2. Дает пользивателю свой инрефейс
        1. Если пользевателя нет в списке бот сообщает и перестает отвечать

    Абривиатуры:
    1. cid == ChatID

    Args:
        message:

    Returns:

    """

    cid = message.chat.id

    user = db.User.objects(usr_id=cid).get()  #FIXME Зачем мне юзер заменить его

    bot.send_message(chat_id=cid, text=f'Привет, {user.name}', reply_markup=InlineKB().generate_kb(category='main_kb'))


@bot.callback_query_handler(func=lambda call: True)
def logic(call):

    user = db.User.objects(usr_id=call.message.chat.id).get()

    moves = {'Премии': ('award', (f'\N{money-mouth face}',
                                  f'\N{neutral face}')
                        ),
             'Задания': ('task', (f'\N{open book}',
                                  f'\N{closed book}')
                         ),
             'Штрафы': ('fine', (f'\N{pouting face}',
                                 f'\N{angry face}')
                        )
             }

    count = getattr(user, f'{moves[call.data][0]}_count')


if __name__ == '__main__':
    bot.polling(none_stop=True)
