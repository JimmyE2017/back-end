from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from app.services.user_services import login, logout


class LoginResource(Resource):
    def post(self):
        data = request.data
        return login(data)


class LogoutResource(Resource):
    @jwt_required
    def delete(self):
        return logout()
