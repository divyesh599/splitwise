# config.py
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///splitwise.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'your_mail_server'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_username'
    MAIL_PASSWORD = 'your_password'