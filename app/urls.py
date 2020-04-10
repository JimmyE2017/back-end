from app.api.ping import PingView
from app.api.v1.coach_views import CoachListView, CoachView
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
        view=CoachListView,
        url="/api/v1/coaches",
        endpoint="coach-list",
        methods=["GET", "POST"],
    ),
    dict(
        view=CoachView,
        url="/api/v1/coaches/<string:coach_id>",
        endpoint="coach",
        methods=["DELETE"],
    ),
]
