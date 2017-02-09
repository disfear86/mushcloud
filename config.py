import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/Database_name'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'dev-key'

ALLOWED_EXTENSIONS = set([
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mkv', 'mov', 'avi', 'mpeg',
                                        'mp4', 'zip', 'rar', 'flac', 'mp3',
                                        'wav'])

USER_STORAGE_PATH = '<Path to your main users storage directory>'

DEBUG = True

MAIL_SERVER = 'smtp.gmail.com' # or your hosts email server
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = '<youremail@host.com>'
MAIL_PASSWORD = '<password>'
MAIL_DEFAULT_SENDER = '<youremail@host.com>'

RESET_PASS_URL = 'http(s)://<yourdomain>/reset_password/'

ADMINS = ['<adminemai@host.com>']
