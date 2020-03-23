from flask import Flask
from flask_restful import Api

from .config import config_by_name
from .urls import urlpatterns


def create_app(config_name="dev"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    app.config.update({"RESTFUL_JSON": dict(indent=2, sort_keys=False, separators=(", ", ": "))})

    # Routing
    api = Api(app)
    for urlpattern in urlpatterns:
        api.add_resource(
            urlpattern["resource"], urlpattern["url"], endpoint=urlpattern["endpoint"]
        )

    return app
