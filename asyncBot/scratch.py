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


import database
from mongoengine.errors import NotUniqueError

from keyboards import InlineKB
from utils import UserStates, ListItem
from messages import MESSAGES

import configparser
# ========================================= Config Sections ===========================================================#
logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)

config = configparser.ConfigParser()
config.read('config.ini')
key = config['API KEYS']['bot_api_key']

bot = Bot(token=key)
dp = Dispatcher(bot, storage=RedisStorage())
dp.middleware.setup(LoggingMiddleware())
# ========================================= Config Sections ===========================================================#

@dp.message_handler(state='*', commands=['start'])
async def start(message: types.Message.from_user.id):
    print('14151515')
    # print(f'id = {id}')
    # if database.User.objects(user_id=user_id).frist():
    #     User(user_id)
    #
    # elif not database.User.objects(user_id=user_id).frist():
    #     await message.reply(MESSAGES['wait_for_name_msg'], reply_markup=InlineKB('main_menu').generate_kb(),
    #                         reply=False, parse_mode=ParseMode.HTML)


class User:

    def __init__(self, id):

        self._user = database.User.objects(user_id=id).get()

        self._id = self._user.user_id
        self._chat_id = self._user.chat_id
        self._name = self._user.name

    def show_menu(self, type):
        pass


class Admin(User):

    def __init__(self, id, chat_id, name):
        super().__init__(id, chat_id, name)

    def show_menu(self, type):
        pass

class Bot:
    pass

class Utils:

    def register(self, user_id, chat_id, name):
        database.User(**{'user_id': user_id, 'chat_id': chat_id, 'name': name}).save()

        try:
            if database.User.objects(user_id=user_id).first():
                # Добавить логи в таком формате [Line | Status | Time | ALL DATA]
                pass

            elif not database.User.objects(user_id=user_id).first():
                # Добавить логи в таком формате [Status | Time | ALL DATA]
                pass

            else:
                # Добавить логи в таком формате [Line | Status | Time | ALL DATA]
                pass
        except Exception:
            # Добавить логи в таком формате [Line | Exception | Time | ALL DATA]
            pass

# import logging
# import random
# import uuid
#
# from aiogram import Bot, Dispatcher, executor, md, types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
# from aiogram.utils.callback_data import CallbackData
# from aiogram.utils.exceptions import MessageNotModified, Throttled
#
# logging.basicConfig(level=logging.DEBUG)
#
# API_TOKEN = '920230310:AAG3M0INv2i65j36nN9fSXjLPQGMgVkf6_E'
#
#
# bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
# storage = MemoryStorage()
# dp = Dispatcher(bot, storage=storage)
# dp.middleware.setup(LoggingMiddleware())
#
# POSTS = {
#     str(uuid.uuid4()): {
#         'title': f'Post {index}',
#         'body': 'Lorem ipsum dolor sit amet, '
#                 'consectetur adipiscing elit, '
#                 'sed do eiusmod tempor incididunt ut '
#                 'labore et dolore magna aliqua',
#         'votes': random.randint(-2, 5),
#     } for index in range(1, 6)
# }
#
# posts_cb = CallbackData('post', 'id', 'action')  # post:<id>:<action>
#
#
# def get_keyboard() -> types.InlineKeyboardMarkup:
#     """
#     Generate keyboard with list of posts
#     """
#     markup = types.InlineKeyboardMarkup()
#     for post_id, post in POSTS.items():
#         markup.add(
#             types.InlineKeyboardButton(
#                 post['title'],
#                 callback_data=posts_cb.new(id=post_id, action='view')),
#         )
#     return markup
#
#
# def format_post(post_id: str, post: dict) -> (str, types.InlineKeyboardMarkup):
#     text = md.text(
#         md.hbold(post['title']),
#         md.quote_html(post['body']),
#         '',  # just new empty line
#         f"Votes: {post['votes']}",
#         sep = '\n',
#     )
#
#     markup = types.InlineKeyboardMarkup()
#     markup.row(
#         types.InlineKeyboardButton('👍', callback_data=posts_cb.new(id=post_id, action='like')),
#         types.InlineKeyboardButton('👎', callback_data=posts_cb.new(id=post_id, action='dislike')),
#     )
#     markup.add(types.InlineKeyboardButton('<< Back', callback_data=posts_cb.new(id='-', action='list')))
#     return text, markup
#
#
# @dp.message_handler(commands='start')
# async def cmd_start(message: types.Message):
#     await message.reply('Posts', reply_markup=get_keyboard())
#
#
# @dp.callback_query_handler(posts_cb.filter(action='list'))
# async def query_show_list(query: types.CallbackQuery):
#     await query.message.edit_text('Posts', reply_markup=get_keyboard())
#
#
# @dp.callback_query_handler(posts_cb.filter(action='view'))
# async def query_view(query: types.CallbackQuery, callback_data: dict):
#     post_id = callback_data['id']
#
#     post = POSTS.get(post_id, None)
#     if not post:
#         return await query.answer('Unknown post!')
#
#     text, markup = format_post(post_id, post)
#     await query.message.edit_text(text, reply_markup=markup)
#
#
# @dp.callback_query_handler(posts_cb.filter(action=['like', 'dislike']))
# async def query_post_vote(query: types.CallbackQuery, callback_data: dict):
#     try:
#         await dp.throttle('vote', rate=1)
#     except Throttled:
#         return await query.answer('Too many requests.')
#
#     post_id = callback_data['id']
#     action = callback_data['action']
#
#     post = POSTS.get(post_id, None)
#     if not post:
#         return await query.answer('Unknown post!')
#
#     if action == 'like':
#         post['votes'] += 1
#     elif action == 'dislike':
#         post['votes'] -= 1
#
#     await query.answer('Vote accepted')
#     text, markup = format_post(post_id, post)
#     await query.message.edit_text(text, reply_markup=markup)
#
#
# @dp.errors_handler(exception=MessageNotModified)
# async def message_not_modified_handler(update, error):
#     return True
#
#
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)