import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__),"."))

class Config(object):
  
  DEBUG = True
  TESTING = False
  ### APP-SETTINGS ###
  VPN_PORT_RANGE = (50000,50100)
  PUBLIC_IP = "192.168.0.66"
  CONTAINER_DIR = "/home/marius/Projects/bachelor/code/containers"
  CLEANUP_BEFORE_AND_AFTER = False
  APP_PREFIX = "vitsl"
  TEMPLATES_AUTO_RELOAD = True
  ### TESTING ###
  USERNAME = "test_user"
  PASSWORD = "123456"

  ### FLASK-SECURITY ###
  SECRET_KEY = "pretty-secret-secret-key"
  SECURITY_USER_IDENTITY_ATTRIBUTES = ('username','email')
  SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
  SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
  SECURITY_CHANGEABLE = True
  SECURITY_REGISTERABLE = False
  SECURITY_RECOVERABLE = False
  #SECURITY_URL_PREFIX = '/auth'
  SECUIRTY_POST_LOGIN = '/'
  SECURITY_POST_LOGOUT_VIEW = '/login'
  SECURITY_POST_LOGIN_VIEW = "/"
  SECURITY_TRACKABLE = False
  SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'    
  SECURITY_PASSWORD_SALT = 'aa0e8ab43c9841f9949e94a3e16f308a'

  SECURITY_MSG_USER_DOES_NOT_EXIST = ('no_user', 'error')
  SECURITY_MSG_INVALID_EMAIL_ADDRESS = ('wrong_user', 'error')
  SECURITY_MSG_INVALID_PASSWORD = ('wrong_pass', 'error')

  ### SQL-ALCHEMY ###
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False
