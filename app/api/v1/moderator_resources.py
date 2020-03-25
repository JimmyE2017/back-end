from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from app.common.access_level import requires_access_level
from app.models.user_model import Roles
from app.services.moderator_services import (
    create_moderator,
    delete_moderator,
    get_all_moderators,
)


class ModeratorListResource(Resource):
    @jwt_required
    @requires_access_level(Roles.PARTICIPANT)
    def get(self):
        return get_all_moderators()

    @jwt_required
    @requires_access_level(Roles.ADMIN)
    def post(self):
        data = request.data
        return create_moderator(data)


class ModeratorResource(Resource):
    @jwt_required
    @requires_access_level(Roles.ADMIN)
    def delete(self, moderator_id):
        return delete_moderator(moderator_id)
