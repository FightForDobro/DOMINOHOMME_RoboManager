import telebot
from keyboards import InlineKB

from template import Content

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

    user = db.User.objects(usr_id=cid).get()  # FIXME Зачем мне юзер заменить его
    
    if user.is_admin():
        bot.send_message(cid, f'Админ панель \N{Gear}',
                         reply_markup=InlineKB().generate_kb(category='admin_kb'))

    else:
        bot.send_message(chat_id=cid, text=f'Привет, {user.name}',
                         reply_markup=InlineKB().generate_kb(category='main_kb'))


@bot.callback_query_handler(func=lambda call: True if call.data == 'back' else False)
def go_back(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.split('-')[0] in ['done', 'not_done'])
def feedback(call):

    cid = call.message.chat.id
    task_id = call.data.split('-')[1]

    if call.data.split('-')[0] == 'done':
        bot.send_message(cid, 'Напишите мне результат:')

    elif call.data.split('-')[0] == 'not_done':
        bot.send_message(cid, 'Почему не получилось:')

    db.User.objects(usr_id=cid).update(step=f'f-{task_id}-{call.data.split("-")[0]}')


@bot.message_handler(func=lambda message: db.User.objects(usr_id=message.chat.id).get().step.split('-')[0] == 'f')
def send_task_feedback(message):

    user = message.chat.id

    if message.text != '0':
        call_data = db.User.objects(usr_id=user).get().step.split('-')
        task_obj = db.Task.objects(owner=db.User.objects(usr_id=user).get())[int(call_data[1])]
        db.AdminMessage().create_message('task', user, call_data[2], message.text, task_obj.content) # TODO в крейте меседже добавить напоминаие админу
        task_obj.erase()

    db.User.objects(usr_id=user).update(step='0')
    bot.send_message(user, 'Главное меню', reply_markup=InlineKB().generate_kb(category='main_kb'))


@bot.message_handler(func=lambda message: db.User.objects(usr_id=message.chat.id).get().step.split('-')[0] == 'a')
def add(message):

    user = db.User.objects(usr_id=message.chat.id).get()

    if message.text != '0':

        data = db.User.objects(usr_id=message.chat.id).get().step.split('-')

        moves = {
            'Премии': user.add_award,
            'Штрафы': user.add_fine,
            'Задания': user.add_task
        }

        moves[data[1]](message.text)

    user.update(step='0')
    bot.send_message(message.chat.id, f'Админ панель \N{Gear}',
                     reply_markup=InlineKB().generate_kb(category='admin_kb'))


@bot.callback_query_handler(func=lambda call: True)
def logic(call):

    if call.data in ['Премии', 'Задания', 'Штрафы']:
        in_task_menu(call.data, call.message.chat.id)
    
    elif call.data.endswith('+'):
        bot.send_message(call.message.chat.id, 'Выберите консультанта',
                         reply_markup=InlineKB().show_users(call.data[:len(call.data) - 1]))

    elif call.data.split('-')[0] == 'add':

        data = call.data.split('-')

        db.User.objects(usr_id=call.message.chat.id).update(step=f'a-{data[1]}-{data[2]}')
        bot.send_message(call.message.chat.id, 'Жду текст:')

    elif call.data == 'Сообщения':
        message = show_admin_message()

        if message is None:  # TODO Поробоавать добавить time.sleep и проверить как он будет спать
            bot.send_message(call.message.chat.id, 'Больше сообщений нет')
            bot.send_message(call.message.chat.id, f'Админ панель \N{Gear}',
                             reply_markup=InlineKB().generate_kb(category='admin_kb'))

        else:
            db.AdminMessage.objects().first().delete()
            bot.send_message(call.message.chat.id,
                             f'Консультант: {message.user.name}\n'
                             f'Категория: {message.category}\n'
                             f'Статус: {message.status}\n'
                             f'Задача: {message.original_text}\n\n'
                             f'Ответ: {message.text}\n\n',
                             reply_markup=InlineKB().message_kb())

    else:
        content(call.data, call.message.chat.id)


def in_task_menu(task_name, cid):

    user = db.User.objects(usr_id=cid).get()

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

    count = getattr(user, f'{moves[task_name][0]}_count')

    task_icon = [f'{moves[task_name][1][0]}' if x < count else f'{moves[task_name][1][1]}' for x in range(7)]

    keyboard = InlineKB().generate_kb(go_back=True, **{f'{moves[task_name][0]}-{b}': f'{b + 1}' for b in range(count)})
    bot.send_message(cid, f'Ваши {task_name}: \n'
                          f'          {"".join(task_icon)} \n'
                          f'Выберите информацию по каждой {task_name} '
                          f'{count} из 7', reply_markup=keyboard)


def content(content_name, cid):

    keyboard = InlineKB().go_back()
    if content_name.split('-')[0] == 'task':
        keyboard = InlineKB().done_or_not(content_name.split('-')[1])

    info = Content(content_name.split('-'), cid).show()

    bot.send_message(cid, f'Информация: \n'
                          f'{info.content}',
                     reply_markup=keyboard)


def show_admin_message():
    return db.AdminMessage.objects().first()


if __name__ == '__main__':
    bot.polling(none_stop=True)
