#!usr/bin/env python
import os
from app import create_app, db
from app.models import Role, User, Day, Pupil_info, Class
from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Role=Role, User=User, Day=Day,
                Pupil_info=Pupil_info, Class=Class)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Start unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

def create_DB():
    db.create_all()
    Role.insert_roles()
    db.session.commit()


@manager.command
def deploy():
    """ Run """
    db.drop_all()
    create_DB()
    app.run()

if __name__ == '__main__':
    manager.run()

