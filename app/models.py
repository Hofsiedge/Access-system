import flask_sqlalchemy
# import sqlalchemy.func.now
from flask_sqlalchemy import SQLAlchemy
from . import db 
# from datetime import datetime, timedelta, time, date
import datetime
# import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import login_manager


class Class(db.Model):
    """ Class, representing the Class model """
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    form = db.Column(db.SmallInteger)
    liter = db.Column(db.String(1))
    form_master = db.Column(db.Integer(), db.ForeignKey('users.id'))
    pupils = db.relationship('Pupil_info', backref='form', lazy='dynamic')
    
    def __repr__(self):
        return ' '.join(map(str, [self.form, self.liter, self.user]))
    

class TimeInside(db.Model):
    """ Time spent at the day by each user """
    __tablename__ = 'timeinside'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date, db.ForeignKey('days.date'))
    total_inside = db.Column(db.Interval)

    @staticmethod
    def compute_total_inside(day=None):
        if day is None:
            day = Day.query.all()[-1]
        passings_dict = {u: [] for u in User.query.all()}
        for passing in Passing.query.filter_by(day=day).all():
            passings_dict[passing.user].append(passing.time)
        for u in passings_dict.keys():
            passings_dict[u] = sum([passings_dict[u][i+1] - passings_dict[u][i] \
                                    for i in range(0, len(passings_dict[u]) // 2)],
                                   datetime.timedelta())
        db.session.add_all([TimeInside(user=u, day=day, total_inside=passings_dict[u]) \
                        for u in passings_dict.keys() if passings_dict[u]])
        db.session.commit()


class User(UserMixin, db.Model):
    """ Class, representing the User model """
    # TODO: Duplication exception processing
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    surname = db.Column(db.String(64))
    name = db.Column(db.String(64))
    patronymic = db.Column(db.String(64))
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))
    passing = db.relationship('Passing', backref='user', lazy='dynamic')
    pupil = db.relationship('Pupil_info', backref='user', lazy='dynamic')
    form = db.relationship('Class', backref='user', lazy='dynamic')
    parent = db.relationship('Parent', backref='user', lazy='dynamic')
    timeinside = db.relationship('TimeInside', backref='user', lazy='dynamic')

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        if self.email == current_app.config['ADMIN']:
            self.role = Role.query.filter_by(name='Admin').first()
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        return True

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True
    
    def can(self, permissions):
        return (self.role.permissions & permissions) == permissions

    def is_administrator(self): 
        return self.can(Permission.A_4 * 2 - 1)

    def ping(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)

    def to_json(self):
        json_user = {
            'url': None,
            'name': self.name,
            'surname': self.surname,
            'patronymic': self.patronymic,
            'id': self.id,
            'last_seen': self.last_seen,
        }
        return json_user

    # TODO: get user information for client method

    @staticmethod
    def create_user(email, name, surname, patronymic, role):
        db.session.add(User(email=email, name=name, surname=surname, \
                            patronymic=patronymic, role=role))
        db.session.commit()

    def __repr__(self):
        return ''.join((self.surname, ' ', self.name[0], '.', \
                        self.patronymic[0], '. ', repr(self.role)))


class Role(db.Model):
    """ Class, representing the Role model (teacher, parent etc)"""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = [
            ('Pupil', Permission.V_1 | Permission.M_1),
            ('Parent', Permission.V_1 | Permission.V_2 | Permission.M_1),
            ('Teacher', Permission.V_1 | Permission.V_2 | Permission.V_3 |
                        Permission.V_4 | Permission.M_2 | Permission.M_3 |
                        Permission.M_4 | Permission.M_5 | Permission.A_1),
            ('Headteacher', Permission.V_1 | Permission.V_2 | Permission.V_3 |
                            Permission.V_4 | Permission.V_5 | Permission.V_6 |
                            Permission.M_2 | Permission.M_3 | Permission.M_4 |
                            Permission.M_5 | Permission.A_1),
            ('Headmaster', Permission.A_3 - 1 - Permission.M_1),
            ('Admin', 2 * Permission.A_4 - 1)
        ]
        for r in roles:
            role = Role.query.filter_by(name=r[0]).first()
            if role is None:
                role = Role(name=r[0])
            role.permissions = r[1]
            db.session.add(role)
            db.session.commit()

    def has_permission(self, permission):
        return self.permissions & permission == permission

    def reset_permissions(self):
        self.permissions = 0

    def remove_permission(self, permission):
        self.permissions &= ~permission

    def add_permission(self, permission):
        self.permissions |= permission

    def __repr__(self):
        return self.name


class Permission:
    # Просматривать посещения:
    V_1 = 0x01 # свои
    V_2 = 0x02 # своих детей
    V_3 = 0x04 # своих учеников
    V_4 = 0x08 # родителей своих учеников
    V_5 = 0x10 # учителей
    V_6 = 0x20 # всех учеников
    V_7 = 0x40 # завучей, директора и прочих
    # Писать: 
    M_1 = 0x80  # классному руководителю
    M_2 = 0x100 # ученикам
    M_3 = 0x200 # родителям
    M_4 = 0x400 # учителям
    M_5 = 0x800 # завучам, директору и прочим
    # Изменять:
    A_1 = 0x1000 # профили учеников своих
    A_2 = 0x2000 # изменять все профили, кроме админского
    A_3 = 0x4000 # изменять сайт
    A_4 = 0x8000 # изменять таблицы


class Pupil_info(db.Model):
    """ Class, representing the Pupil_info model """
    __tablename__ = 'pupil_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    form_id = db.Column(db.SmallInteger, db.ForeignKey('classes.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))

    @staticmethod
    def connect_pupil_info(user, form):
        """ Attach pupil_info to the pupil """
        db.session.add(Pupil_info(user=user, form=form))
        db.session.commit()

    def __repr__(self):
        return ' '.join(map(str, [self.user, self.form.form, self.form.liter]))


class Parent(db.Model):
    """ Class, representing the Parent model """
    __tablename__ = 'parents' 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pupils = db.relationship('Pupil_info', backref='parent')

    @staticmethod
    def connect_child(user_parent, pupil):
        """ Create a parent user """
        pupil.parent_id = user_parent.id
        db.session.add_all([Parent(user=user_parent), pupil])
        db.session.commit()


class Passing(db.Model):
    __tablename__ = 'passings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date, db.ForeignKey('days.date'))
    time = db.Column(db.DateTime)

    # TODO: Check
    @staticmethod
    def create_passing(user_id, day, time=None):  
        """ Register passing """
        assert user_id is not None
        user = User.query.get(user_id)
        if time is None:
            time = datetime.datetime(2018, 1, 1, *datetime.datetime.now().timetuple()[3:6])
        if type(time) is not datetime.time:
            time = datetime.datetime(2018, 1, 1, *time)
        if day is None:
            day = Day.query.all()[-1]
        else:
            day = Day.query.filter_by(date=datetime.date(*day)).first()
        db.session.add(Passing(user=user, day=day, time=time))
        db.session.commit()

    def __repr__(self):
        return ' '.join([repr(self.day), str(self.time), repr(self.user)])


class Day(db.Model):
    __tablename__ = 'days'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    passing = db.relationship('Passing', backref='day', lazy='dynamic')
    timeinside = db.relationship('TimeInside', backref='day', lazy='dynamic')

    @staticmethod
    def create_day(date=datetime.date(*datetime.datetime.now().timetuple()[0:3])):
        if type(date) is not datetime.date:
            assert date is not None
            date = datetime.date(*date)
        db.session.add(Day(date=date))
        db.session.commit()

    def save_day(self):
        """ Compute total_inside for each user at the last day and save it """
        pass

    def __repr__(self):
        return str(self.date)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# TODO: check query optimization

def repr_history():
    pass

