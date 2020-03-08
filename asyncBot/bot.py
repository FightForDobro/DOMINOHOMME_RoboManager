import asyncio
import logging
import emoji
from datetime import datetime

import aioredis
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.contrib.fsm_storage.redis import RedisStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import database as db
from mongoengine.errors import NotUniqueError

from keyboards import InlineKB
from utils import UserStates, ListItem
from messages import MESSAGES

from random import choice
import logging
import configparser
#

# ========================================= Memory Storage ============================================================#
user_messages_to_delete = {}
# ========================================= Memory Storage ============================================================#

# ========================================= Config Sections ===========================================================#
logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)
log = logging.getLogger('broadcast')

config = configparser.ConfigParser()
config.read('config.ini')
key = config['API KEYS']['bot_api_key']

bot = Bot(token=key)
dp = Dispatcher(bot, storage=RedisStorage())
dp.middleware.setup(LoggingMiddleware())
# ========================================= Config Sections ===========================================================#

# ========================================= Bot Logic Section =========================================================#
@dp.message_handler(state='*', commands=['start'])
async def process_start_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    if db.User.objects(user_id=message.from_user.id).first() is None:
        await state.set_state('wait_for_name')
        user_messages_to_delete[message.from_user.id] = [(await message.reply(text(emojize(
                                MESSAGES['wait_for_name_msg'].format(name=message.from_user.full_name))),
                                reply=False, parse_mode=ParseMode.HTML,
                                reply_markup=InlineKB().if_name_suit_btn(message.from_user.full_name)))]

    else:

        if not db.User.objects(user_id=message.from_user.id).get().verified:
            await bot.send_message(message.chat.id, 'Чтобы продолжить работу с ботом, напишите @DOMINOkaty')

        else:
            await User(**get_user_data(message.from_user.id)).send_keyboard('main_menu')

@dp.message_handler(state='*', commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Привет!\nНапиши мне что-нибудь!")


@dp.message_handler(state=UserStates.WAIT_FOR_NAME)
async def register(message):

    if type(message) == types.Message:
        await User(message.chat.id, message.from_user.id, message.text).register()

    elif type(message) == types.CallbackQuery:
        await User(message.from_user.id, message.from_user.id, message.data).register()

    else:
        print(f'Type: {type(message)} not correct\n Possible types: {types.Message} and {types.CallbackQuery}')


@dp.message_handler(state='*', content_types=ContentType.ANY)
async def catch_user_input(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    if 'admin_add' in await state.get_state():
        state_data = await state.get_data()
        user = db.User.objects(user_id=state_data["user_id"]).get()
        getattr(user, state_data['operation'])(message.text)

        await User(**get_user_data(message.from_user.id)).send_keyboard('main_menu')

    elif 'admin_broadcast' in await state.get_state():
        users = db.User.objects()

        for user in users:

            if message.photo:
                photo = await message.photo[-1].get_url()
                await bot.send_photo(user.chat_id, types.InputFile.from_url(photo), message.caption)

            elif message.text:
                await bot.send_message(user.chat_id, message.text)

            else:
                log.info(f'STATUS: Error | USER: {message.from_user.id} | ACTION: Broadcast | Exception: Not Valid Type'
                         f'| Message Type: {type(message)}')

        await User(**get_user_data(message.from_user.id)).send_keyboard('main_menu')

    elif 'wait_for_result' in await state.get_state():
        state_data = await state.get_data()

        admins = db.User.objects(admin=True)
        user = db.User.objects(user_id=message.from_user.id).get()
        point = db.Points.objects(id=state_data['point_id']).get()

        result = 'Выполнено' if state_data['delete'] else 'Не выполнено'

        for admin in admins:
            await bot.send_message(admin.chat_id, f'Консультант: {user.name}\n\nЗадание: {point.content}\n\n'
                                                  f'Статус: {result}\n\nОтветил: {message.text}')
        if state_data['delete']:
            point.delete()

@dp.callback_query_handler(state='*')
async def catch_callback(call: types.CallbackQuery):
    state = dp.current_state(user=call.from_user.id)

    if await state.get_state() == 'wait_for_name':
        await bot.answer_callback_query(call.id)
        await register(call)

    elif call.data.split('_to_')[0] == 'back':
        await bot.answer_callback_query(call.id)
        await User(**get_user_data(call.from_user.id)).send_keyboard(call.data.split('_to_')[1])

    elif call.data in ['yes', 'no']:
        await bot.answer_callback_query(call.id)
        await User(**get_user_data(call.from_user.id)).in_task_menu(call.data)

    elif call.data == 'broadcast':
        await bot.answer_callback_query(call.id)
        await User(**get_user_data(call.from_user.id)).admin_broadcast()

    elif await state.get_state() == 'admin_menu':
        await bot.answer_callback_query(call.id)
        await User(**get_user_data(call.from_user.id)).show_admin_sub_menu(call.data)

    elif 'admin_add' in await state.get_state():
        await bot.answer_callback_query(call.id)
        await User(**get_user_data(call.from_user.id)).admin_add(call.data)

    elif call.data.split('_')[0] == 'edit':
        await bot.answer_callback_query(call.id)
        if call.data.split('_')[1] == 'topics':
            await bot.send_message('Напиши мне новую тему дня:')

    elif call.data in ['award', 'remind', 'task', 'topics', 'training', 'fine']:
        await bot.answer_callback_query(call.id)
        await User(**get_user_data(call.from_user.id)).show_user_sub_menu(call.data)

    elif call.data.split('_')[0] in ['award', 'remind', 'topics', 'training', 'fine']:
        point = db.Points.objects(id=call.data.split('_')[1]).get()
        await bot.answer_callback_query(call.id, point.content, True)

    elif call.data.split('_')[0] == 'task':
        await bot.answer_callback_query(call.id)
        await User(**get_user_data(call.from_user.id)).task_menu(call.data)

    else:
        print(call.data)


class User:

    def __init__(self, chat_id, user_id, name, admin=False, verified=False):

        self._chat_id = chat_id
        self._id = user_id
        self._name = name
        self._admin = admin
        self._verified = verified

        self._state = dp.current_state(user=user_id)

    async def send_keyboard(self, keyboard: str):

        if not await self.check_verification_status():
            return

        if user_messages_to_delete.get(self._id, 0) == 0:
            user_messages_to_delete[self._id] = []

        await self.delete_old_messages()

        keyboards_titles = {
            'main_menu': 'Главное меню 🖥️',
            'admin_menu': 'Админ меню ⚙'
        }

        if self._admin:
            keyboard = 'admin_menu'

        await self._state.set_state(keyboard)

        user_messages_to_delete[self._id].extend((

            await bot.send_message(self._chat_id, MESSAGES['daily_topic'].format(
                                   topic=db.BotTexts.objects().first().daily_topic)),

            await bot.send_message(self._chat_id, MESSAGES['birthdays'].format(get_birthdays())),

            await bot.send_message(self._chat_id, keyboards_titles[keyboard],
                                   reply_markup=InlineKB(keyboard).generate_kb()))
        )

    async def show_user_sub_menu(self, menu_tittle):

        if not await self.check_verification_status():
            return

        await self.delete_old_messages()
        tittles_definitions = {'award': 'Премий', 'remind': 'Напоминаний', 'fine': 'Штрафов',
                               'task': 'Заданий', 'topics': 'Тем дня', 'training': 'Обучений'}

        user = db.User.objects(user_id=self._id).get()
        points = db.Points.objects(type=menu_tittle, owner=user)
        user_messages_to_delete[self._id] = [(await bot.send_message(self._chat_id,
                                              f'У тебя {points.count()} {tittles_definitions[menu_tittle]}\n'
                                              f'Нажми на кнопки снизу, чтобы ознакомиться',
                                              reply_markup=InlineKB().pointers_buttons(points)))]

    async def register(self):

        try:

            db.User(**{'user_id': self._id, 'chat_id': self._chat_id, 'name': self._name, 'verified': False}).save()
            await bot.send_message(self._chat_id, f'{self._name}, Добро пожаловать!🤘\n'
                                                  f'Напиши @DOMINOkaty чтобы продолжить работу с ботом')
            await self._state.set_state('wait_for_verified')

        except NotUniqueError:
            user_messages_to_delete[self._id] = [(await bot.send_message(
                                                 self._chat_id, 'Это имя уже занято😥\n Попробуй другое'))]

    async def show_admin_sub_menu(self, data):

        if not await self.check_verification_status():
            return

        await self.delete_old_messages()
        await self._state.set_state(f'admin_{data}')

        moves = {'add': 'Добавить ➕', 'edit': 'Изменить 🖊', 'broadcast': 'Вещать 📯'}

        user_messages_to_delete[self._id] = [(await bot.send_message(self._chat_id, moves[data],
                                             reply_markup=getattr(InlineKB(), f'admin_{data}')()))]

    async def admin_edit(self, data):

        if not await self.check_verification_status():
            return

        await self.delete_old_messages()

        user_messages_to_delete[self._id] = [(await bot.send_message(self._chat_id, 'Изменить 🖊',
                                                                     reply_markup=InlineKB('main_menu').generate_kb()))]

    async def admin_add(self, data):

        if not await self.check_verification_status():
            return

        await self.delete_old_messages()

        if data.split('_')[0] == 'user':
            await self._state.update_data({'user_id': data.split('_')[1]})
            user_messages_to_delete[self._id] = [(await bot.send_message(self._chat_id, 'Напиши комментарий:'))]

        else:
            await self._state.set_state(UserStates.ADMIN_ADD)
            await self._state.set_data({'operation': data})

            user_messages_to_delete[self._id] = [(await bot.send_message(
                self._chat_id, 'Выбери консультанта:',
                reply_markup=InlineKB().get_user_buttons(db.User.objects(admin__ne=True))))]

    async def edit_topic(self):

        if not await self.check_verification_status():
            return

        await self.delete_old_messages()
        await self._state.set_state('admin_edit_topic')

    async def admin_broadcast(self):

        if not await self.check_verification_status():
            return

        await self.delete_old_messages()
        await self._state.set_state('admin_broadcast')
        user_messages_to_delete[self._id] = [(await bot.send_message(self._chat_id,
                                                                     'Напиши мне что-ты, хочешь сказать:'))]

    async def task_menu(self, data):

        if not await self.check_verification_status():
            return

        await self.delete_old_messages()

        point = db.Points.objects(id=data.split('_')[1]).get()
        await self._state.set_data({'point_id': str(point.id)})

        user_messages_to_delete[self._id] = [(await bot.send_message(self._chat_id, point.content,
                                                               reply_markup=InlineKB('done_or_not', 2).generate_kb()))]

    async def in_task_menu(self, data):

        if not await self.check_verification_status():
            return

        await self.delete_old_messages()

        state_data = await self._state.get_data()
        await self._state.set_state('wait_for_result')
        await self._state.set_data(state_data)

        if data == 'yes':
            user_messages_to_delete[self._id] = [(await bot.send_message(self._chat_id,
                                                                         'Напиши результат:'))]
            await self._state.update_data({'delete': True})

        else:
            user_messages_to_delete[self._id] = [(await bot.send_message(self._chat_id, 'Почему?'))]
            await self._state.update_data({'delete': False})

    async def delete_old_messages(self):

        messages = user_messages_to_delete[self._id]

        for message in messages:

            try:

                user_messages_to_delete[self._id].pop(0)
                await message.delete()

            except MessageToDeleteNotFound:  # Добавить сюда логи
                print(user_messages_to_delete)
                print(message)

    async def check_verification_status(self):

        if not self._verified:
            jokes = [f'{self._name}, Я же попросил написать @DOMINOkaty',
                     f'{self._name}, прекратите нажимать кнопки\n Лучшим решением будет написать @DOMINOkaty',
                     f'{self._name}, Вам стоит написать @DOMINOkaty']

            await bot.send_message(self._chat_id, choice(jokes))
            return False

        return True
# =====================================================================================================================#

# ================================================== Utils ============================================================#
async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

def get_user_data(user_id):
    user = db.User.objects(user_id=user_id).get()
    return {'user_id': user_id, 'chat_id': user.chat_id, 'name': user.name,
            'admin': user.admin, 'verified': user.verified}


def get_birthdays():

    birthday_boys = []
    for client in db.Clients.objects():

        try:
            if client.birthday == 'нет':
                continue

            elif client.birthday.month == datetime.now().date().month and client.birthday.day == datetime.now().day:
                birthday_boys.append(f'{client.name}: {client.phone}\n')
        except AttributeError:
            print(client.id)
            print(client.name)
            print(client.birthday)

    if not birthday_boys:
        birthday_boys.append('Сегодня нет клиентов, у которых день рождения пора найти новых клиентов')

    return ''.join(birthday_boys)
# =====================================================================================================================#


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)
