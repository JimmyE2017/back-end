from flask import jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app.services.user_services import (
    forgotten_password,
    get_me,
    login,
    logout,
    update_password,
)


class LoginView(MethodView):
    def post(self):
        data = request.data
        response, code = login(data)
        return make_response(jsonify(response), code)


class LogoutView(MethodView):
    @jwt_required
    def delete(self):
        response, code = logout()
        return make_response(jsonify(response), code)


class UserMeView(MethodView):
    @jwt_required
    def get(self):
        response, code = get_me()
        return make_response(jsonify(response), code)


class ForgottenPasswordView(MethodView):
    def post(self):
        data = request.data
        response, code = forgotten_password(data)
        return make_response(jsonify(response), code)


class ResetPasswordView(MethodView):
    def post(self):
        response, code = update_password(params=request.args, data=request.data)
        return make_response(jsonify(response), code)
