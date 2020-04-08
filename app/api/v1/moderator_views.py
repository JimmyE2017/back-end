from flask import jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app.common.access_level import requires_access_level
from app.models.user_model import Roles
from app.services.moderator_services import (
    create_moderator,
    delete_moderator,
    get_all_moderators,
)


class ModeratorListView(MethodView):
    @jwt_required
    @requires_access_level(Roles.MODERATOR)
    def get(self):
        response, code = get_all_moderators()
        return make_response(jsonify(response), code)

    @jwt_required
    @requires_access_level(Roles.ADMIN)
    def post(self):
        data = request.data
        response, code = create_moderator(data)
        return make_response(jsonify(response), code)


class ModeratorView(MethodView):
    @jwt_required
    @requires_access_level(Roles.ADMIN)
    def delete(self, moderator_id):
        response, code = delete_moderator(moderator_id)
        return make_response(jsonify(response), code)
