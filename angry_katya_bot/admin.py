import db

db.User.objects(usr_id=157301758).get().add_task('Набрать клиента')
