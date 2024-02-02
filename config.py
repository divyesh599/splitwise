# config.py
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///splitwise.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'divyeshsatyukt@gmail.com'
    MAIL_PASSWORD = 'AdivyeshLIB1'
    MAIL_DEBUG = True
