from flask import jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app.common.access_level import requires_access_level
from app.models.user_model import Roles
from app.services.action_card_services import (
    get_all_action_cards,
    get_coach_action_card_batches,
    update_coach_action_card_batches,
)


class ActionCardListView(MethodView):
    @jwt_required
    @requires_access_level(Roles.COACH)
    def get(self):
        response, code = get_all_action_cards()
        return make_response(jsonify(response), code)


class ActionCardBatchView(MethodView):
    @jwt_required
    @requires_access_level(Roles.COACH)
    def get(self, coach_id):
        response, code = get_coach_action_card_batches(coach_id)
        return make_response(jsonify(response), code)

    @jwt_required
    @requires_access_level(Roles.COACH)
    def put(self, coach_id):
        response, code = update_coach_action_card_batches(coach_id, request.data)
        return make_response(jsonify(response), code)
