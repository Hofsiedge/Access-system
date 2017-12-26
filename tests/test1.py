import unittest
from flask import current_app
from app import create_app, db
from app.models import Role, User, Class, Parent, Pupil_info, \
        create_user, save_pass, create_parent, connect_pupil_info


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
        create_user('vasya_pupkin', 'Вася', 'Пупкин', 'Алексеевич', None)
        save_pass(User.query.filter_by(username='vasya_pupkin').first().id)

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
