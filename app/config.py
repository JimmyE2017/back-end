import datetime
import os


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious_secret_key")
    JWT_SECRET_KEY = SECRET_KEY
    DEBUG = False
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "")
    JSON_SORT_KEYS = False

    # Flask-JWT-Extended
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access"]
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=2)

    # Flask Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_TLS = bool(int(os.getenv("MAIL_USE_TLS", 0)))
    MAIL_USE_SSL = bool(int(os.getenv("MAIL_USE_SSL", 0)))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER") or MAIL_USERNAME
    MAIL_SUPPRESS_SEND = True  # Prevent from sending email


class LocalConfig(Config):
    DEBUG = True
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    MONGODB_DB = os.getenv("MONGODB_DB")
    MONGODB_HOST = os.getenv("MONGODB_HOST")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT"))


class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    MONGODB_DB = os.getenv("MONGODB_DB")
    MONGODB_HOST = os.getenv("MONGODB_HOST")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT"))


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGODB_SETTINGS = {"db": "test", "host": "mongomock://localhost"}


class ProductionConfig(Config):
    DEBUG = False
    MAIL_SUPPRESS_SEND = False
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    MONGODB_DB = os.getenv("MONGODB_DB")
    MONGODB_HOST = os.getenv("MONGODB_HOST")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT"))


config_by_name = dict(
    local=LocalConfig, dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig
)

key = Config.SECRET_KEY
