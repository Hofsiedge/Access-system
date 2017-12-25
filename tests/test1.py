import unittest
from flask import current_app
from app import create_app, db
from app.models import Role, User, Class, create_user, save_pass

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

    def test_roles_initializing(self):
        admin = Role(name='Admin')
        teacher = Role(name='Teacher')
        pupil = Role(name='Pupil')
        parent = Role(name='Parent')
        db.session.add_all([admin, teacher, pupil, parent])
        db.session.commit()
        
    def test_user_creating(self):
        self.test_roles_initializing()
        teacher = Role.query.filter_by(name='Teacher').first()
        create_user('vasya_pupkin', 'Вася', 'Пупкин', 'Алексеевич', teacher)

    def test_classes_creation(self):
        create_user('vasya_pupkin', 'Вася', 'Пупкин', 'Алексеевич',
                    Role.query.filter_by(name='Teacher').first())
        class10A = Class(form=10, liter='A', user=User.query.filter_by(id=1).first())
        
    def test_pass(self):
        create_user('vasya_pupkin', 'Вася', 'Пупкин', 'Алексеевич',
                    Role.query.filter_by(name='Teacher').first())
        save_pass(User.query.filter_by(username='vasya_pupkin').first().id)

