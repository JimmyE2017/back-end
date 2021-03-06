from app.api.ping import PingView
from app.api.v1.action_card_views import ActionCardBatchView, ActionCardListView
from app.api.v1.carbon_forms_views import CarbonFormAnswersView
from app.api.v1.coach_views import CoachListView, CoachView
from app.api.v1.user_views import (
    ForgottenPasswordView,
    LoginView,
    LogoutView,
    ResetPasswordView,
    UserMeView,
)
from app.api.v1.workshop_views import (
    WorkshopListView,
    WorkshopParticipantListView,
    WorkshopParticipantView,
    WorkshopView,
)

urlpatterns = [
    dict(view=PingView, url="/api/ping", endpoint="ping", methods=["GET"]),
    dict(view=LoginView, url="/api/v1/login", endpoint="login", methods=["POST"]),
    dict(view=LogoutView, url="/api/v1/logout", endpoint="logout", methods=["DELETE"]),
    dict(view=UserMeView, url="/api/v1/users/me", endpoint="get-me", methods=["GET"]),
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
        methods=["GET", "DELETE"],
    ),
    dict(
        view=ActionCardListView,
        url="/api/v1/action_cards",
        endpoint="action-cards-list",
        methods=["GET"],
    ),
    dict(
        view=ActionCardBatchView,
        url="/api/v1/coaches/<string:coach_id>/action_card_batches",
        endpoint="action-cards-batch-list",
        methods=["GET", "PUT"],
    ),
    dict(
        view=WorkshopListView,
        url="/api/v1/workshops",
        endpoint="workshop-list",
        methods=["GET", "POST"],
    ),
    dict(
        view=WorkshopView,
        url="/api/v1/workshops/<string:workshop_id>",
        endpoint="workshop",
        methods=["DELETE", "GET"],
    ),
    dict(
        view=WorkshopParticipantListView,
        url="/api/v1/workshops/<string:workshop_id>/participants",
        endpoint="workshop-participant-list",
        methods=["POST"],
    ),
    dict(
        view=WorkshopParticipantView,
        url="/api/v1/workshops/<string:workshop_id>/"
        "participants/<string:participant_id>",
        endpoint="workshop-participant",
        methods=["DELETE"],
    ),
    dict(
        view=CarbonFormAnswersView,
        url="/api/v1/carbon_forms/<string:workshop_id>",
        endpoint="carbon-forms",
        methods=["POST"],
    ),
]
