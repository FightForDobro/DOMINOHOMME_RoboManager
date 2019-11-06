from mongoengine import *
import json

connect('angrykaty')


class User(Document):

    usr_id = IntField(unique=True, required=True)
    name = StringField(max_length=64, required=True,unique=True)
    fine_count = IntField(default=0)
    award_count = IntField(default=0)
    task_count = IntField(default=0)

    def add_fine(self, text):

        fine_obj = {
            'content': text,
            'owner': self
        }

        self.update(inc__fine_count=1)

        Fine(**fine_obj).save()

    def add_award(self, text):

        award_obj = {
            'content': text,
            'owner': self
        }

        self.update(inc__award_count=1)

        Award(**award_obj).save()

    def add_task(self, text):

        task_obj = {
            'content': text,
            'owner': self
        }

        self.update(inc__task_count=1)

        Task(**task_obj).save()


class Fine(Document):
    content = StringField()
    owner = ReferenceField(User)

    def delete_fine(self):

        User.objects(id=self.owner.id).update(dec__fine_count=1)
        self.delete()


class Award(Document):
    content = StringField()
    owner = ReferenceField(User)

    def delete_award(self):

        User.objects(id=self.owner.id).update(dec__award_count=1)
        self.delete()


class Task(Document):
    content = StringField()
    owner = ReferenceField(User)

    def delete_task(self):

        User.objects(id=self.owner.id).update(dec__task_count=1)
        self.delete()


# user_dict = {
#     'usr_id': 0,
#     'name': 'Anna',
# }
#
# User(**user_dict).save()
#
# user = User.objects(usr_id=157301758).get()

# user.add_fine('Some text for fines')
# user.add_award('Some text for new award')
# user.add_task('Some task')

# fine = Task.objects(id='5dc0a540eda7911507ad64bc').get()
#
# fine.delete_task()

# user_id = Fine.objects(owner='5dc0a540eda7911507ad64b9').get()
#
# print(user_id.owner.id)
#
# user = User.objects(usr_id=157301758).get()
# print(user)

# award = Award.objects(owner=user)
# print(award.to_json(indent=3))
# print(award.as_pymongo())
#
# text =

# print(award[1])
