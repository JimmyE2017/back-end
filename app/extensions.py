from flask import jsonify, make_response

from app.common.errors import (
    ExpiredTokenError,
    InvalidTokenError,
    RevokedTokenError,
    UnauthorizedTokenError,
)
from app.models.user_model import BlacklistTokenModel, UserModel


def setup_jwt(jwt):
    # Custom method for checking blacklist token
    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token: dict) -> bool:
        jti = decrypted_token["jti"]
        return BlacklistTokenModel.is_jti_blacklisted(jti)

    @jwt.unauthorized_loader
    def unauthorized_callback(msg: str) -> (dict, int):
        e = UnauthorizedTokenError()
        return make_response(jsonify(e.get_content()), e.code)

    @jwt.expired_token_loader
    def expired_token_callback(msg: str) -> (dict, int):
        e = ExpiredTokenError()
        return make_response(jsonify(e.get_content()), e.code)

    @jwt.invalid_token_loader
    def invalid_token_callback(msg: str) -> (dict, int):
        e = InvalidTokenError()
        return make_response(jsonify(e.get_content()), e.code)

    @jwt.revoked_token_loader
    def revoked_token_callback() -> (dict, int):
        e = RevokedTokenError()
        return make_response(jsonify(e.get_content()), e.code)

    @jwt.user_loader_callback_loader
    def get_user_from_identity(user_id: str) -> UserModel:
        return UserModel.find_by_id(user_id)
