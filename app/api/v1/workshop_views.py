from flask import jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app.common.access_level import requires_access_level
from app.models.user_model import Roles
from app.services.workshop_services import (
    create_workshop,
    delete_workshop,
    get_workshop,
    get_workshops,
)


class WorkshopListView(MethodView):
    @jwt_required
    @requires_access_level(Roles.COACH)
    def get(self):
        response, code = get_workshops()
        return make_response(jsonify(response), code)

    @jwt_required
    @requires_access_level(Roles.COACH)
    def post(self):
        data = request.data
        response, code = create_workshop(data)
        return make_response(jsonify(response), code)


class WorkshopView(MethodView):
    @jwt_required
    @requires_access_level(Roles.COACH)
    def delete(self, workshop_id):
        response, code = delete_workshop(workshop_id=workshop_id)
        return make_response(jsonify(response), code)

    @jwt_required
    @requires_access_level(Roles.COACH)
    def get(self, workshop_id):
        response, code = get_workshop(workshop_id=workshop_id)
        return make_response(jsonify(response), code)
