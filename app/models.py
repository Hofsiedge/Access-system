import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from . import db 
from datetime import datetime


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    patronymic = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    day = db.relationship('Day', backref='user', lazy='dynamic')
    pupil = db.relationship('Pupil_info', backref='user', lazy='dynamic')
    form = db.relationship('Class', backref='user', lazy='dynamic')

    def __repr__(self):
        return self.username


class Day(db.Model):
    __tablename__ = 'day'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.Time())

    def __repr__(self):
        return ' - '.join([str(self.user), str(self.time)])


class Pupil_info(db.Model):
    __tablename__ = 'pupil_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    form_id = db.Column(db.SmallInteger, db.ForeignKey('classes.id'))
    #form = db.Column(db.SmallInteger)
    #liter = db.Column(db.String(1))

    def __repr__(self):
        return ' '.join(map(str, [self.user, self.form.form, self.form.liter]))


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    form = db.Column(db.SmallInteger)
    liter = db.Column(db.String(1))
    form_master = db.Column(db.Integer(), db.ForeignKey('users.id'))
    pupils = db.relationship('Pupil_info', backref='form', lazy='dynamic')
    
    def __repr__(self):
        return ' '.join(map(str, [self.form, self.liter, self.user]))
    

#class Parent_info(db.Model):
    #TODO: Complete
    #pass

def connect_pupil_info(user, form):
    db.session.add(Pupil_info(user=user, form=form))
    db.session.commit()

def save_pass(user_id):  
    '''
        Регистрирует проход
        user_id: int
    '''
    user = User.query.filter_by(id=user_id).first()
    db.session.add(Day(user=user, time=datetime.time(datetime.now())))
    db.session.commit()

def create_user(username, name, surname, patronymic, role):
    db.session.add(User(username=username, name=name, patronymic=patronymic,\
                        role=role))
    db.session.commit()
 
