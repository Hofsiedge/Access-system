import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from . import db 
from datetime import datetime, timedelta
import sqlite3


class Role(db.Model):
    """ Class, representing the Role model (teacher, parent etc)"""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return self.name


class User(db.Model):
    """ Class, representing the User model """
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
        return ' '.join([self.name, self.surname, self.patronymic, repr(self.role)])


class Day(db.Model):
    """
    Class, representing the Day model
    The Day table contains passings for each user
    """
    __tablename__ = 'day'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.Time())

    def __repr__(self):
        return ' - '.join([str(self.user), str(self.time)])
    

class Pupil_info(db.Model):
    """ Class, representing the Pupil_info model """
    __tablename__ = 'pupil_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    form_id = db.Column(db.SmallInteger, db.ForeignKey('classes.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'))

    def __repr__(self):
        return ' '.join(map(str, [self.user, self.form.form, self.form.liter]))


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
    

class Parent(db.Model):
    """ Class, representing the Parent model """
    __tablename__ = 'parents' 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    pupils = db.relationship('Pupil_info', backref='parent')


# TODO: Transactions
def process_day(users, day):

    """
    Process the day, return a dict with necessary information
    (first and last passing time, total time inside (hours, minutes))
    """

    A = {} # dict for the time information

    for user_id in users:
        A[user_id] = []

    for passing in day:
        A[passing.user_id].append(passing.time)

    for user_id in A.keys():

        if A[user_id]:
            first_passing = A[user_id][0] #save first and last passings
            last_passing = A[user_id][-1]

        if len(A[user_id]) % 2: # delete last passing,
            del A[user_id][-1]  # if it's not paired

        for passing_num in range(len(A[user_id])//2):
            a = A[user_id][passing_num]
            a = datetime(2000, 1, 1, a.hour, a.minute, a.second)
            b = A[user_id][passing_num + 1]
            b = datetime(2000, 1, 1, b.hour, b.minute, b.second)
            A[user_id][passing_num : passing_num + 2] = [b - a]

        if A[user_id]:
            total_time = timedelta(0)
            for time in A[user_id]:
                total_time += time
            A[user_id] = first_passing, last_passing, \
                    ':'.join(map(str, (total_time.seconds // 3600, \
                                       total_time.seconds % 3600 // 60, total_time.seconds % 60)))

    A = {user_id: A[user_id] for user_id in A.keys() if A[user_id]}
    return A 

def save_day():

    """ Write the day to the history table """

    users = [i.id for i in User.query.all()]
    day = Day.query.all()
    pre_history = process_day(users, day)

    con = sqlite3.connect('history.sqlite')
    cur = con.cursor()
    #
    # TODO: REMOVE WHEN END DEBUGING!!!
    # cur.execute('DROP TABLE history;')
    #
    cur.execute("""SELECT name FROM sqlite_master
                WHERE type='table' AND name='history';""")

    if not cur.fetchall():
        cur.execute("""CREATE TABLE history 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_id INTEGER UNIQUE);""")
        for i in users:
            cur.execute('INSERT INTO history VALUES (NULL, ?);', (i,))
        con.commit()
    
    current_date = '_'.join(map(str, datetime.now().timetuple()[2::-1]))

    cur.execute("ALTER TABLE history ADD COLUMN %s TEXT;" % ('f_' + current_date)) 
    cur.execute("ALTER TABLE history ADD COLUMN %s TEXT;" % ('l_' + current_date)) 
    cur.execute("ALTER TABLE history ADD COLUMN %s TEXT;" % ('t_' + current_date)) 
    # first, last, total

    for i in pre_history.keys():
        cur.execute("""UPDATE history SET 
                    %s=? WHERE user_id=?;""" % ('f_' + current_date), \
                    (str(pre_history[i][0])[:8], i))
        cur.execute("""UPDATE history SET 
                    %s=? WHERE user_id=?;""" % ('l_' + current_date), \
                    (str(pre_history[i][1])[:8], i))
        cur.execute("""UPDATE history SET 
                    %s=? WHERE user_id=?;""" % ('t_' + current_date), \
                    (pre_history[i][2], i))
    con.commit()
    for i in Day.query.all():
        db.session.delete(i)
    db.session.commit()
    return 'The day is over'


def repr_history(day, month, year, column='flt'):
    """ Return history for the required date """
    current_date = '_'.join(map(str, (day, month, year)))
    f, l, t = 'f_' + current_date, 'l_' + current_date, 't_' + current_date
    # first, last, total
    cur = sqlite3.connect('history.sqlite').cursor()
    query_list = ['user_id']
    if 'f' in column:
        query_list.append(f)
    if 'l' in column:
        query_list.append(l)
    if 't' in column:
        query_list.append(t)
    cur.execute('SELECT %s FROM history;' % \
                (', '.join(query_list)))
    return cur.fetchall()

def get_dates():
    conn = sqlite3.connect('history.sqlite')
    cur = conn.cursor()
    t = cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND tbl_name='history';").fetchone()
    dates = [i.split('_')[1:] for i in t[0][126:-1].split()[::6]]
    return dates

def create_parent(user_parent, pupil):
    """ Create a parent user """
    pupil.parent_id = user_parent.id
    db.session.add_all([Parent(user=user_parent), pupil])
    db.session.commit()

def connect_pupil_info(user, form):
    """ Attach pupil_info to the pupil """
    db.session.add(Pupil_info(user=user, form=form))
    db.session.commit()

def save_pass(user_id):  
    """ Register passing """
    user = User.query.filter_by(id=user_id).first()
    db.session.add(Day(user=user, time=datetime.time(datetime.now())))
    db.session.commit()

def create_user(username, name, surname, patronymic, role):
    db.session.add(User(username=username, name=name, surname=surname, \
                        patronymic=patronymic, role=role))
    db.session.commit()
 
