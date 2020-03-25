from app.api.ping import PingResource
from app.api.v1.moderator_resources import ModeratorListResource, ModeratorResource
from app.api.v1.user_resources import LoginResource, LogoutResource

urlpatterns = [
    dict(resource=PingResource, url="/api/ping", endpoint="ping"),
    dict(resource=LoginResource, url="/api/v1/login", endpoint="login"),
    dict(resource=LogoutResource, url="/api/v1/logout", endpoint="logout"),
    dict(
        resource=ModeratorListResource,
        url="/api/v1/moderators",
        endpoint="moderator-list",
    ),
    dict(
        resource=ModeratorResource,
        url="/api/v1/moderators/<int:moderator_id>",
        endpoint="moderator",
    ),
]
