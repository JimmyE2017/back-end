from flask import jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app.common.access_level import requires_access_level
from app.models.user_model import Roles
from app.services.coach_services import (
    create_coach,
    delete_coach,
    get_all_coachs,
    get_coach,
)


class CoachListView(MethodView):
    @jwt_required
    @requires_access_level(Roles.COACH)
    def get(self):
        response, code = get_all_coachs()
        return make_response(jsonify(response), code)

    @jwt_required
    @requires_access_level(Roles.ADMIN)
    def post(self):
        data = request.data
        response, code = create_coach(data)
        return make_response(jsonify(response), code)


class CoachView(MethodView):
    @jwt_required
    @requires_access_level(Roles.ADMIN)
    def delete(self, coach_id):
        response, code = delete_coach(coach_id)
        return make_response(jsonify(response), code)

    @jwt_required
    @requires_access_level(Roles.COACH)
    def get(self, coach_id):
        response, code = get_coach(coach_id)
        return make_response(jsonify(response), code)
