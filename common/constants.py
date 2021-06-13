import datetime
import os

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = os.environ.get('DB_NAME')
APP_SECRET_KEY = os.environ.get('SECRET_KEY')
API_ERROR_STATUS = 'Internal Server Error'
API_SUCCESS_STATUS = 'OK'
JWT_REFRESH_TOKEN_TIMEDELTA = datetime.timedelta(hours=24)
JWT_ACCESS_TOKEN_TIMEDELTA = datetime.timedelta(minutes=15)