import datetime
import os


# TODO : Add env file
class Config:
    SECRET_KEY = os.getenv("CAPLC_SECRET_KEY", "my_precious_secret_key")
    JWT_SECRET_KEY = SECRET_KEY
    DEBUG = False
    RESTFUL_JSON = dict(indent=2, sort_keys=False, separators=(", ", ": "))
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access"]
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=2)
    MONGODB_USERNAME = os.getenv("CAPLC_MONGODB_USERNAME")
    MONGODB_PASSWORD = os.getenv("CAPLC_MONGODB_PASSWORD")
    MONGODB_DB = os.getenv("CAPLC_MONGODB_DB")
    MONGODB_HOST = os.getenv("CAPLC_MONGODB_HOST")
    MONGODB_PORT = int(os.getenv("CAPLC_MONGODB_PORT"))
    MONGODB_AUTHENTICATION_SOURCE = "test"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGODB_DB = Config.MONGODB_DB + "Test"


class ProductionConfig(Config):
    DEBUG = False


config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)

key = Config.SECRET_KEY
