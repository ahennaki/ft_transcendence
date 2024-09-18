
from django.urls    import path
from .consumers     import FriendshipRequestConsumer

websocket_urlpatterns = [
    path('ws/friendship-request/', FriendshipRequestConsumer.as_asgi()),
]
