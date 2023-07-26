"""Flask configuration."""
from os import environ, path
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

TESTING = True
DEBUG = True
FLASK_ENV = 'development'
#SECRET_KEY = environ.get('SECRET_KEY')
SECRET_KEY = '*AE442079E16316383EDCC6A5E9CBE6015E522350'


DBCONFIG = {
    #'host': '172.22.41.13',
    # Desktop on ZT:
    #'host': '172.22.19.3',
    #'host': '192.168.0.100',
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'deiper2401$',
    'database': 'sigptar'
}
