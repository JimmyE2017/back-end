from app.api.ping import PingResource
from app.api.v1.moderator_resources import ModeratorListResource, ModeratorResource
from app.api.v1.user_resources import (
    ForgottenPasswordResource,
    LoginResource,
    LogoutResource,
    ResetPasswordResource,
)

urlpatterns = [
    dict(resource=PingResource, url="/api/ping", endpoint="ping"),
    dict(resource=LoginResource, url="/api/v1/login", endpoint="login"),
    dict(resource=LogoutResource, url="/api/v1/logout", endpoint="logout"),
    dict(
        resource=ForgottenPasswordResource,
        url="/api/v1/forgotten_password",
        endpoint="forgotten-password",
    ),
    dict(
        resource=ResetPasswordResource,
        url="/api/v1/reset_password",
        endpoint="reset-password",
    ),
    dict(
        resource=ModeratorListResource,
        url="/api/v1/moderators",
        endpoint="moderator-list",
    ),
    dict(
        resource=ModeratorResource,
        url="/api/v1/moderators/<string:moderator_id>",
        endpoint="moderator",
    ),
]
