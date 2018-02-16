import unittest
from flask import current_app
from app import create_app, db
from app.models import Role, User, Class, Parent, Pupil_info, Day, \
        create_user, save_pass, create_parent, connect_pupil_info, \
        save_day, repr_history
from time import sleep


class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])

    def test_classes_creation(self):
        create_user('vasya_pupkin', 'Вася', 'Пупкин', 'Алексеевич',
                    Role.query.filter_by(name='Teacher').first())
        class10A = Class(form=10, liter='A', user=User.query.filter_by(id=1).first())
        
    def test_pass(self):
        create_user('vasya_pupkin', 'Вася', 'Пупкин', 'Алексеевич', None)
        save_pass(User.query.filter_by(username='vasya_pupkin').first().id)


class ParentModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_parent_creation(self):
        create_user('parent_1', 'Вася', 'Пупкин', 'Алексеевич', None)
        class10A = Class(form=10, liter='A', user=User.query.filter_by(id=1).first())
        pupil = Role(name='Pupil')
        db.session.add(class10A, pupil)
        db.session.commit()
        create_user('pupil_1', 'Вася', 'Пупкин', 'Алексеевич', pupil)
        connect_pupil_info(User.query.filter_by(id=2).first(), class10A)
        create_parent(User.query.filter_by(id=1).first(),
                      Pupil_info.query.filter_by(id=1).first())
        assert Pupil_info.query.filter_by(id=1).first().parent.id == 1
        assert Parent.query.filter_by(user_id=1).first().pupils[0] == \
                Pupil_info.query.filter_by(id=1).first()


class RolesModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_roles_initializing(self):
        admin = Role(name='Admin')
        teacher = Role(name='Teacher')
        pupil = Role(name='Pupil')
        parent = Role(name='Parent')
        db.session.add_all([admin, teacher, pupil, parent])
        db.session.commit()

class HistoryDBTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_history_update(self):
        pupil = Role(name='Pupil')
        create_user('vasya_pupkin', 'Вася', 'Пупкин', 'Алексеевич', pupil)
        create_user('anatoly_123', 'Анатолий', 'Какой-то', 'Батькович', pupil)
        save_pass(1)
        sleep(1)
        save_pass(2)
        sleep(1)
        save_pass(2)
        sleep(1)
        save_pass(2)
        sleep(1)
        save_pass(1)
        sleep(1)
        save_pass(2)
        save_pass(1)
        save_pass(2)
        save_day()

class UserModelTestCase(unittest.TestCase):
    def test_user_creating(self):
        self.test_roles_initializing()
        teacher = Role.query.filter_by(name='Teacher').first()
        create_user('vasya_pupkin', 'Вася', 'Пупкин', 'Алексеевич', teacher)

    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('not a cat'))
    
    def test_salts_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u1.password_hash != u2.password_hash)
