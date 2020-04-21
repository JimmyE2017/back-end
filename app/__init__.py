from flask import Flask, jsonify, make_response
from flask_jwt_extended import JWTManager

from app.cli import cli_commands
from app.common.errors import CustomException

from .config import config_by_name
from .extensions import setup_jwt
from .urls import urlpatterns


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
