import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'Avb4jb?!kfasfGhm./1ihVl,ёdgnvz2xo9 s'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite') 
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
