from app.api.ping import PingView
from app.api.v1.moderator_views import ModeratorListView, ModeratorView
from app.api.v1.user_views import (
    ForgottenPasswordView,
    LoginView,
    LogoutView,
    ResetPasswordView,
)

urlpatterns = [
    dict(view=PingView, url="/api/ping", endpoint="ping", methods=["GET"]),
    dict(view=LoginView, url="/api/v1/login", endpoint="login", methods=["POST"]),
    dict(view=LogoutView, url="/api/v1/logout", endpoint="logout", methods=["DELETE"]),
    dict(
        view=ForgottenPasswordView,
        url="/api/v1/forgotten_password",
        endpoint="forgotten-password",
        methods=["POST"],
    ),
    dict(
        view=ResetPasswordView,
        url="/api/v1/reset_password",
        endpoint="reset-password",
        methods=["POST"],
    ),
    dict(
        view=ModeratorListView,
        url="/api/v1/moderators",
        endpoint="moderator-list",
        methods=["GET", "POST"],
    ),
    dict(
        view=ModeratorView,
        url="/api/v1/moderators/<string:moderator_id>",
        endpoint="moderator",
        methods=["DELETE"],
    ),
]
