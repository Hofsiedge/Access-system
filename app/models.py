import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from . import db 
from datetime import datetime
import re
import sqlite3


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
    parent = db.relationship('Parent', backref='user', lazy='dynamic')

    def __repr__(self):
        return self.username


class Day(db.Model):
    __tablename__ = 'day'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.Time())

    def __repr__(self):
        return ' - '.join([str(self.user), str(self.time)])
    

#class History(db.Model):
    #__tablename__ = 'history'
    #id = db.Column(db.Integer, primary_key = True)
    #user_id = db.Column(db.Integer, unique=True)
    #separate columns for each day are to create by save_day function


#def save_day():
    #users = Day.query.all()
    #History.
    #for user in users:
        
def save_day():
    con = sqlite3.connection('history.sqlite')
    cur = con.cursor()
    cur.execute("""SELECT name FROM sqlite_master"
                WHERE type='table' AND name='history';""")

    users = [i.id for i in User.query.all()]

    if not cur.fetchall():
        cur.execute("""CREATE TABLE history 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_id INTEGER UNIQUE;""")
        for i in range(len(users)):
            cur.execute('INSERT INTO history VALUES (NULL, ?);', (i,))
        con.commit()
    
    day = Day.query.all()
    pre_history = {}

    for i in users:
        pre_history[i] = []

    for i in day:
        pre_history[i.user_id].append(i.time)

    for i in range(len(pre_history)):
        #Здесь хранится время пребывания в лицее
        if len(pre_history[i])%2 != 0:
            print('Кто-то не покинул лицей или не отметил уход')
        for q in range(pre_history[i]//2):
            pre_history[i][q:q+1] = str(pre_history[i][q+1]-pre_history[i][q])
            #TODO: Заменить pre_history[i] на интересующие результаты

    for i in pre_history.keys:
        if not pre_history[i]:
            del pre_history[i]

    current_date = '.'.join(map(str, datetime.datetime.now().timetuple()[2::-1]))

    cur.execute("ALTER TABLE history ADD COLUMN ? TEXT;",
                (current_date, ))
    for i in pre_history.keys:
        cur.execute("UPDATE history SET ?=? WHERE user_id=?;", 
                    (current_date, pre_history[i], i))
#TODO: Maybe it's reasonable to split this function on save_day and process_day


class Pupil_info(db.Model):
    __tablename__ = 'pupil_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    form_id = db.Column(db.SmallInteger, db.ForeignKey('classes.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))

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
    

class Parent(db.Model):
   __tablename__ = 'parents' 
   id = db.Column(db.Integer, primary_key=True)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
   pupils = db.relationship('Pupil_info', backref='parent')


def create_parent(user_parent, pupil):
    pupil.parent_id = user_parent.id
    db.session.add_all([Parent(user=user_parent), pupil])
    db.session.commit()

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
 
