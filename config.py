import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    CSRF_ENABLED = True
# TODO: permanent environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db_repository')
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465 
    # MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    # FIXME: С пробелами работает криво
    MAIL_SENDER = 'Контроль посещаемости <zuev.ilia.al@yandex.ru>'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # MAIL_SUBJECT_PREFIX = 'Контроль&#160;посещаемости&#160;'
    MAIL_SUBJECT_PREFIX = '&#160;'
    ADMIN = os.environ.get('ADMIN')

    POSTGRES_URL = os.environ.get("POSTGRES_URL")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PW = os.environ.get("POSTGRES_PW")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    POSTGRES_DB = os.environ.get("POSTGRES_DEV_DB")
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=Config.POSTGRES_USER, \
                                                                   pw=Config.POSTGRES_PW, \
                                                                   url=Config.POSTGRES_URL, \
                                                                   db=POSTGRES_DB)

# TODO: switch other DBs to PostgreSQL

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'data-test.sqlite') 


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'data.sqlite') 


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
