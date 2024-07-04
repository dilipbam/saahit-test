import os
from dotenv import load_dotenv
SERVICE_ROOT = os.path.dirname(__file__)
ENV_FILE_PATH = os.path.join(SERVICE_ROOT, '.env')

load_dotenv(ENV_FILE_PATH)
DB_SERVER = os.environ['DB_SERVER']
DATABASE = os.environ['DATABASE']
DB_HOST = os.environ['DB_HOST']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_PORT = os.environ['DB_PORT']

EMAIL = os.environ['EMAIL']
EMAIL_APP_PASSWORD = os.environ['EMAIL_APP_PASSWORD']

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA_PATH = os.path.join(APP_ROOT, os.environ['MEDIA_DIR'])

DB_URL = "{server}://{username}:{password}@{host}:{port}/{db}" \
    .format(server=DB_SERVER, username=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, db=DATABASE, port=DB_PORT)