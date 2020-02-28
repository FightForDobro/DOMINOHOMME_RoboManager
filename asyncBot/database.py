from mongoengine import *
from bot_exceptions import FatalException

connect('domino_bot_db')


class User(DynamicDocument):

    user_id = IntField(unique=True, required=True)
    chat_id = IntField(required=True)
    name = StringField(max_length=64, required=True, unique=True)
    admin = BooleanField(default=False)
    admin_level = IntField(default=0)
    verified = BooleanField(default='False')

    def add_award(self, content):

        Points(**{'type': 'award',
                  'content': content,
                  'owner': self}).save()

    def add_fine(self, content):

        Points(**{'type': 'fine',
                  'content': content,
                  'owner': self}).save()

    def add_task(self, content):

        Points(**{'type': 'task',
                  'content': content,
                  'owner': self}).save()

    def add_remind(self, content):

        Points(**{'type': 'remind',
                  'content': content,
                  'owner': self}).save()

    def add_courses(self, content):

        Points(**{'type': 'courses',
                  'content': content,
                  'owner': self}).save()

    @classmethod
    def get_users_verification_status(cls):
        return {'verified_users': cls.objects(verified=True),
                'not_verified_users': cls.objects(verified=False)}

    def approve_user(self):

        if not self.verified:

            self.verified = True
            self.save()

            if self.verified:
                return True

            else:
                # TODO Добавить логи
                raise FatalException('Если это произошло срочно пишите вашему администратору')

        else:
            raise ValueError(f'{self.name} уже верифицирован')

    def block_user(self):

        if self.verified:

            self.verified = False
            self.save()

            if not self.verified:
                return True

            else:
                # TODO Добавить логи
                raise FatalException('Если это произошло срочно пишите вашему администратору')

        else:
            raise ValueError(f'{self.name} уже заблокирован')


class Points(DynamicDocument):

    type = StringField(required=True)
    content = StringField(required=True)
    owner = ReferenceField('User')

class BotTexts(Document):
    daily_topic = StringField()


class Clients(Document):

    name = StringField(required=True)
    phone = StringField()
    birthday = DateTimeField()
    employee = StringField()
    size = StringField()


# user_dict = {
#     'chat_id': 415151551,
#     'user_id': 157301762,
#     'name': 'Sveta',
#     'admin': False,
# }
#
# User(**user_dict).save()
#
#
# BotTexts(**{'daily_topics': 'Бот работает, клиенты приходят!'}).save() mongoengine.errors.NotUniqueError


# user = User.objects(user_id=157301758).first()
# print(user)
# user.add_award('Пришел твой клиент')

# Clients(**{'client_id': 1, 'name': 'Kateryna Shukhnina',
#            'phone': '380968920623', 'birthday': datetime.now().date()}).save()

# if Clients.objects(client_id=0).get().birthday.date() == datetime.now().date():
#     print('Done!')

# def get_birthdays():
#     birthday_boys = []
#     for client in Clients.objects(birthday=datetime.now().date()):
#         birthday_boys.append((client.name, client.phone))
#
#
#     print(birthday_boys)
#
#
# get_birthdays()
#
# user = User.objects(name='Deny2s').first()
# print(user.name)