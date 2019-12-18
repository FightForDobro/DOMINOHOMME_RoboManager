import telebot
from telebot.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
import keyboards
from keyboards import InlineKB
from config import TOKEN
import db

bot = telebot.TeleBot(TOKEN)

know_users = []
user_step = {}


def get_user_in_db():

    return [u.name for u in db.User.objects]


def get_menu_buttons_definition():

    return ['Премии', 'Задания', 'Штрафы']


def get_user_step(uid):
    if uid in user_step:
        return user_step[uid]

    else:
        know_users.append(uid)
        user_step[uid] = 0
        return 0


@bot.message_handler(commands=['start'])
def start(message):
    cid = message.chat.id

    if cid not in know_users:
        know_users.append(cid)
        user_step[cid] = 0

        bot.send_message(message.chat.id, 'Привет я злая катя напиши свое имя!')

        keyboard = InlineKB().generate_kb(*get_user_in_db(), **{'admin_login': 'ADMIN'})

        # keyboard = InlineKeyboardMarkup()
        # buttons = [InlineKeyboardButton(f'{b}', callback_data=str(b)) for b in users_in_db]
        # buttons.append(InlineKeyboardButton('ADMIN', callback_data='admin_login'))
        # keyboard.add(*buttons)

        bot.send_message(message.chat.id, 'AUTH', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: get_user_step(call.message.chat.id) == 0)
def login(call):

    if db.User.objects(name__iexact=call.data):

        db.User.objects(name__iexact=call.data).update(usr_id=call.message.chat.id)

        bot.send_message(call.message.chat.id, f'Привет {call.data}')

        keyboard = InlineKB().generate_kb(*get_menu_buttons_definition())

        # keyboard = InlineKeyboardMarkup()
        # buttons = [InlineKeyboardButton(f'{b}', callback_data=str(b)) for b in ['Премии', 'Задания', 'Штрафы']]
        # keyboard.add(*buttons)


        bot.send_message(call.message.chat.id, 'MENU', reply_markup=keyboard)

        user_step[call.message.chat.id] = 1

    elif call.data == 'admin_login':

        bot.send_message(call.message.chat.id, f'Введите пароль:')

        @bot.message_handler(func=lambda message: True)
        def admin_menu(message):

            bot.send_message(message.chat.id, f'Пивет Админ :)')

            # keyboard_a = InlineKeyboardMarkup()
            # buttons_a = [InlineKeyboardButton(f'{b}', callback_data=str(b)) for b in users_in_db]
            # keyboard_a.add(*buttons_a)

            keyboard_a = InlineKB().generate_kb(*get_user_in_db())

            bot.send_message(message.chat.id, 'ADMIN MENU', reply_markup=keyboard_a)
            user_step[call.message.chat.id] = 'a'

            @bot.callback_query_handler(func=lambda a_call: get_user_step(call.message.chat.id) == 'a')
            def admin_logic(a_call):
                bot.send_message(call.message.chat.id, f'Вы вибрали {a_call.data}')


    else:

        bot.send_message(call.message.chat.id, f'{call.data} Тебя нет в списке :( \n'
                                               f'напиши мне @DOMINOkaty')
        user_step[call.message.chat.id] = 0


@bot.callback_query_handler(func=lambda call: get_user_step(call.message.chat.id) == 1)
def logic(call):

    if call.data == 'Премии':

        count = db.User.objects(usr_id=call.message.chat.id).get().award_count

        award_icon = [f'\N{money-mouth face}' if x < count else f'\N{neutral face}' for x in range(7)]

        keyboard = InlineKB().generate_kb(**{f'award-{b}': f'{b + 1}' for b in range(count)})

        bot.send_message(call.message.chat.id, f'Ваши премии: \n'
                                               f'          {"".join(award_icon)} \n'
                                               f'Выберите информацию по каждой премии: \n'
                                               f'{count} из 7', reply_markup=keyboard)
        user_step[call.message.chat.id] = 'award'

    elif call.data == 'Задания':

        count = db.User.objects(usr_id=call.message.chat.id).get().task_count

        task_icon = [f'\N{open book}' if x < count else f'\N{closed book}' for x in range(7)]

        keyboard = InlineKB().generate_kb(**{f'task-{b}': f'{b + 1}' for b in range(count)})

        bot.send_message(call.message.chat.id, f'Ваши задачи: \n'
                                               f'          {"".join(task_icon)} \n'
                                               f'Выберите информацию по каждому заданию: \n'
                                               f'{count} из 7', reply_markup=keyboard)
        user_step[call.message.chat.id] = 'task'

    elif call.data == 'Штрафы':

        count = db.User.objects(usr_id=call.message.chat.id).get().fine.count

        task_icon = [f'\N{pouting face}' if x < count else f'\N{angry face}' for x in range(7)]

        keyboard = InlineKB().generate_kb(**{f'fine-{b}': f'{b + 1}' for b in range(count)}, *{''})

        bot.send_message(call.message.chat.id, f'Ваши штрафы: \n'
                                               f'          {"".join(task_icon)} \n'
                                               f'Веберите информацию по каждому штрафу'
                                               f'{count} из 7', reply_markup=keyboard)
        user_step[call.message.chat.id] = 'fine'


@bot.callback_query_handler(func=lambda call: get_user_step(call.message.chat.id) == 'award')
def award_content(call):

    keyboard = InlineKB().generate_kb(**{'Премии': '<-- Назад <--'})

    award_info = db.Award.objects(owner=db.User.objects(usr_id=call.message.chat.id).get())[int(call.data.split('-')[-1])]
    bot.send_message(call.message.chat.id, f'Информация: \n'
                                           f'{award_info.content} \n', reply_markup=keyboard)

    user_step[call.message.chat.id] = 1


@bot.callback_query_handler(func=lambda call: get_user_step(call.message.chat.id) == 'fine')
def fine_content(call):

    fine_info = db.Fine.objects(owner=db.User.objects(usr_id=call.message.chat.id).get())[int(call.data.split('-')[-1])]
    bot.send_message(call.message.chat.id, f'Информация: \n'
                                           f'{fine_info.content} \n')


@bot.callback_query_handler(func=lambda call: get_user_step(call.message.chat.id) == 'task')
def task_content(call):
    task_info = db.Task.objects(owner=db.User.objects(usr_id=call.message.chat.id).get())[int(call.data.split('-')[-1])]
    bot.send_message(call.message.chat.id, f'Информация: \n'
                                           f'{task_info.content} \n')


bot.polling(none_stop=True)


# print(get_user_in_db())
