from app.common.errors import (
    EXPIRED_TOKEN,
    INVALID_TOKEN,
    REVOKED_TOKEN,
    UNAUTHORIZED_TOKEN,
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
        return UNAUTHORIZED_TOKEN.get_error()

    @jwt.expired_token_loader
    def expired_token_callback(msg: str) -> (dict, int):
        return EXPIRED_TOKEN.get_error()

    @jwt.invalid_token_loader
    def invalid_token_callback(msg: str) -> (dict, int):
        return INVALID_TOKEN.get_error()

    @jwt.revoked_token_loader
    def revoked_token_callback() -> (dict, int):
        return REVOKED_TOKEN.get_error()

    @jwt.user_loader_callback_loader
    def get_user_from_identity(user_id: str) -> UserModel:
        return UserModel.find_by_id(user_id)
