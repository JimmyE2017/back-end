from .api.ping import PingResource

urlpatterns = [dict(resource=PingResource, url="/api/ping", endpoint="ping")]
