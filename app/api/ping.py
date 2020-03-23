from flask_restful import Resource


class PingResource(Resource):
    def get(self):
        response = {"data": "pong"}

        return response, 200
