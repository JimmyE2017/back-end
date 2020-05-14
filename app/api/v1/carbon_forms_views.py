from flask import jsonify, make_response, request
from flask.views import MethodView

from app.services.carbon_forms_services import create_carbon_form_answers


class CarbonFormAnswersView(MethodView):
    def post(self, workshop_id):
        data = request.data
        response, code = create_carbon_form_answers(workshop_id=workshop_id, data=data)
        return make_response(jsonify(response), code)
