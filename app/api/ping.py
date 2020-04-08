from flask import jsonify, make_response
from flask.views import MethodView


class PingView(MethodView):
    def get(self):
        response = {"data": "pong"}

        return make_response(jsonify(response), 200)
