from flask import jsonify, make_response
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app.common.access_level import requires_access_level
from app.models.user_model import Roles
from app.services.action_card_services import get_all_action_cards


class ActionCardListView(MethodView):
    @jwt_required
    @requires_access_level(Roles.COACH)
    def get(self):
        response, code = get_all_action_cards()
        return make_response(jsonify(response), code)
