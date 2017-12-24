import os
from datetime import datetime
from time import sleep

from flask import Flask, render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required, Email
from flask_migrate import Migrate, MigrateCommand, migrate

import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

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
        return ' - '.join([str(self.user.id), str(self.time)])


class Pupil_info(db.Model):
    __tablename__ = 'pupil_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    form_cypher = db.Column(db.SmallInteger, db.ForeignKey('classes.id'))
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
    

def connect_pupil_info(user, form):
    db.session.add(Pupil_info(user=user, form=form, liter=liter))
    db.session.commit()

def save_changes():
    migrate()

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
    
# TODO: Сделать вариант сайта для админов
# TODO: Добавить в .vimrc навигацию в режиме вставки


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[Required()])
    surname = StringField('Фамилия', validators=[Required()])
    patronymic = StringField('Отчество', validators=[Required()])
    username = StringField('Логин', validators=[Required()])
    email = StringField('Адрес электронной почты', validators=[Email()])
    role =  SelectField('Кто Вы?', choices=[('3', 'Ученик'), \
                       ('4', 'Родитель'), ('2', 'Учитель')])
    submit = SubmitField('Подтвердить')
# TODO: Написать дополнительную форму для Parent

#class Hist(db.Model):
#    pass

db.drop_all()
db.create_all()

#connect_pupil_info(User.query.filter_by(id=1).first(), 10, 'A')

#print(os.path.abspath(os.path.dirname(__file__)))

#admin = Role.query.filter_by(name='Admin').first()
#teacher = Role.query.filter_by(name='Teacher').first()
#pupil = Role.query.filter_by(name='Pupil').first()
#parent = Role.query.filter_by(name='Parent').first()

admin = Role(name='Admin')
teacher = Role(name='Teacher')
pupil = Role(name='Pupil')
parent = Role(name='Parent')

create_user('vasya_pupkin1', 'Вася', 'Пупкин', 'Алексеевич', teacher)
create_user('vasya_pupkin2', 'Вася', 'Пупкин', 'Алексеевич', teacher)
create_user('vasya_pupkin3', 'Вася', 'Пупкин', 'Алексеевич', teacher)
create_user('vasya_pupkin4', 'Вася', 'Пупкин', 'Алексеевич', teacher)
create_user('vasya_pupkin5', 'Вася', 'Пупкин', 'Алексеевич', teacher)

db.session.add_all([admin, teacher, pupil, parent])
db.session.commit()

class10A = Class(form=10, liter='A', user=User.query.filter_by(id=1).first())
class10B = Class(form=10, liter='Б', user=User.query.filter_by(id=2).first())
class10C = Class(form=10, liter='В', user=User.query.filter_by(id=3).first())
class11A = Class(form=11, liter='A', user=User.query.filter_by(id=4).first())
class11B = Class(form=11, liter='Б', user=User.query.filter_by(id=5).first())
db.session.add(class10A)
db.session.commit()


#save_pass(3)
#
print(Role.query.all())
print(User.query.all())
print(Day.query.all())
print(Pupil_info.query.all())
print(Class.query.all())


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        form.username.data = ''
        name = form.name.data
        form.name.data = ''
        surname = form.surname.data
        form.surname.data = ''
        patronymic = form.patronymic.data
        form.patronymic.data = ''

        role = Role.query.filter_by(id=int(form.role.data)).first()
        create_user(username, name, surname, patronymic, role)
        return redirect(url_for('registration'))
    return render_template('registration.html', form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/table')
def show_table():
    return render_template('show_table.html')

if __name__ == '__main__':
    manager.run()

