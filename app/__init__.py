import datetime
import json

from flask import Flask, jsonify, make_response
from flask_jwt_extended import JWTManager
from mongoengine.base.document import BaseDocument
from mongoengine.fields import DBRef, ObjectId
from mongoengine.queryset.base import BaseQuerySet

from app.cli import cli_commands
from app.common.errors import CustomException

from .config import config_by_name
from .extensions import setup_jwt
from .urls import urlpatterns


class MongoEngineEncoder(json.JSONEncoder):
    """Handles Encoding of ObjectId's"""

    def default(self, obj, **kwargs):
        if isinstance(obj, BaseQuerySet):
            return [d.to_mongo() for d in obj]
        elif isinstance(obj, BaseDocument):
            return obj.to_mongo()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, DBRef):
            return {
                "collection": obj.collection,
                "id": str(obj.id),
                "database": obj.database,
            }
        return json.JSONEncoder.default(self, obj)


def _register_view(app, view, endpoint, url, methods):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, view_func=view_func, methods=methods)


def create_app(config_name="dev"):
    from app.models import db
    from app.common.mail import mail

    app = Flask(__name__)

    # Load config
    app.config.from_object(config_by_name[config_name])

    # Setup DB
    db.init_app(app)

    # Setup Flask-JWT-extended
    jwt = JWTManager(app)
    setup_jwt(jwt)
    jwt.init_app(app)

    # Setup Flask-Mail
    mail.init_app(app)

    # Setup custom json encoder
    app.json_encoder = MongoEngineEncoder

    # Setup custom error handler
    @app.errorhandler(CustomException)
    def handle_exception(e):
        return make_response(jsonify(e.get_content()), e.code)

    # Routing
    for urlpattern in urlpatterns:
        _register_view(app, **urlpattern)

    for cli_cmd in cli_commands:
        app.cli.add_command(cli_cmd)

    return app
