import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__),"."))

class Config(object):
  
  DEBUG = True
  TESTING = False
  ### APP-SETTINGS ###
  HINT_TIMEOUT = 15
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
  SECURITY_USER_IDENTITY_ATTRIBUTES = ('username')
  SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
  SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
  SECURITY_CHANGEABLE = True
  SECURITY_REGISTERABLE = True
  SECURITY_RECOVERABLE = False
  SECURITY_LOGIN_USER_TEMPLATE = 'login_user.jinja'
  SECURITY_REGISTER_USER_TEMPLATE = 'register_user.jinja'


  #SECURITY_URL_PREFIX = '/auth'
  SECUIRTY_POST_LOGIN = '/'
  SECURITY_POST_LOGOUT_VIEW = '/login'
  SECURITY_POST_LOGIN_VIEW = "/"
  SECURITY_TRACKABLE = False
  SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'    
  SECURITY_PASSWORD_SALT = 'aa0e8ab43c9841f9949e94a3e16f308a'

  SECURITY_MSG_USER_DOES_NOT_EXIST = ('Username or password are incorrect.', 'error')
  SECURITY_MSG_INVALID_EMAIL_ADDRESS = ('Username or password are incorrect.', 'error')
  SECURITY_MSG_INVALID_PASSWORD = ('Username or password are incorrect.', 'error')

  ### SQL-ALCHEMY ###
  #mysql://ic_user:pZ9yHYZnV3JchsdxpEcNqVknUP5YwwwfMfEjK8b4942vKRwU6g9q748TkdMabw3M@192.168.0.66:3307/issue_collector_master
  #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/vitsl"
  SQLALCHEMY_TRACK_MODIFICATIONS = False
