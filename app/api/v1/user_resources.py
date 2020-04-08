from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from app.services.user_services import (
    forgotten_password,
    login,
    logout,
    update_password,
)


class LoginResource(Resource):
    def post(self):
        data = request.data
        return login(data)


class LogoutResource(Resource):
    @jwt_required
    def delete(self):
        return logout()


class ForgottenPasswordResource(Resource):
    def post(self):
        data = request.data
        return forgotten_password(data)


class ResetPasswordResource(Resource):
    def post(self):
        return update_password(params=request.args, data=request.data)
