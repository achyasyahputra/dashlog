import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DEBUG = os.environ['DEBUG']
PORT = os.environ['PORT']
ES_HOST = os.environ['ES_HOST']
ES_PORT = os.environ['ES_PORT']
INDEX_NAME = os.environ['INDEX_NAME']
SECRET_KEY = os.environ['SECRET_KEY']
AUTH_REDIRECT_URI = os.environ['AUTH_REDIRECT_URI']
BASE_URI = os.environ['BASE_URI']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
DOMAIN_NAME = os.environ['DOMAIN_NAME']
EXCLUDE_EMAIL = os.environ['EXCLUDE_EMAIL']