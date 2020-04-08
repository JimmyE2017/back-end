import datetime
import json

from flask import Flask, make_response
from flask_jwt_extended import JWTManager
from flask_restful import Api
from mongoengine.base.document import BaseDocument
from mongoengine.fields import DBRef, ObjectId
from mongoengine.queryset.base import BaseQuerySet

from .config import config_by_name
from .extensions import setup_jwt
from .urls import urlpatterns


class MongoEngineEncoder(json.JSONEncoder):
    """Handles Encoding of ObjectId's"""

    def default(self, obj, **kwargs):

        if isinstance(obj, datetime.datetime):
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

    # Routing URLs
    api = Api(app)
    for urlpattern in urlpatterns:
        api.add_resource(
            urlpattern["resource"], urlpattern["url"], endpoint=urlpattern["endpoint"]
        )

    # JSON Output
    @api.representation("application/json")
    def output_json(data, code, headers=None):
        """Makes a Flask response with a JSON encoded body"""
        if isinstance(data, BaseQuerySet):
            json_data = json.dumps([d.to_mongo() for d in data], cls=MongoEngineEncoder)

        elif isinstance(data, BaseDocument):
            json_data = json.dumps(data.to_mongo(), cls=MongoEngineEncoder)
        else:
            json_data = json.dumps(data)
        resp = make_response(json_data, code)
        resp.headers.extend(headers or {})
        return resp

    return app
