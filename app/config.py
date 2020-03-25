import datetime
import os

# uncomment the line below for postgres database url from environment variable

basedir = os.path.abspath(os.path.dirname(__file__))


# TODO : Add env file
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious_secret_key")
    JWT_SECRET_KEY = SECRET_KEY
    DEBUG = False
    RESTFUL_JSON = dict(indent=2, sort_keys=False, separators=(", ", ": "))
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access"]
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=2)


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    MONGODB_SETTINGS = {
        "db": "caplcDevDB",
        "host": "mongodb://caplc_user:password123@127.0.0.1:27017/caplcDevDB",
    }


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGODB_SETTINGS = {
        "db": "caplcTestDB",
        "host": "mongodb://caplc_user:password123@127.0.0.1:27017/caplcTestDB",
    }


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    MONGODB_SETTINGS = {"db": "caplc", "host": os.getenv("MONGO_URI", "")}


config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)

key = Config.SECRET_KEY
