from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from .config import config_by_name
from .extensions import setup_jwt
from .urls import urlpatterns


def create_app(config_name="dev"):
    from app.models import db

    app = Flask(__name__)

    # Load config
    app.config.from_object(config_by_name[config_name])

    # Setup DB
    db.init_app(app)

    # Setup JWT-extended
    jwt = JWTManager(app)
    setup_jwt(jwt)
    jwt.init_app(app)

    # Routing
    api = Api(app)
    for urlpattern in urlpatterns:
        api.add_resource(
            urlpattern["resource"], urlpattern["url"], endpoint=urlpattern["endpoint"]
        )

    return app
