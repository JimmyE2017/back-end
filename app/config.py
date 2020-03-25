import datetime
import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']

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
    SQLALCHEMY_DATABASE_URI = "postgresql://user_test:password@localhost:5432/caplc_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://user_test:password@localhost:5432/test_caplc_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)

key = Config.SECRET_KEY
