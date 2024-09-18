from rest_framework                 import generics, status
from django.http                    import JsonResponse
from authentication.utils           import Authenticate
from channels.layers                import get_channel_layer
from asgiref.sync                   import async_to_sync
from ..models                       import FriendRequest, Profile
from ..utils.connections_manager    import connected_clients, clients_lock 

class HandleFriendshipRequestView(generics.GenericAPIView):
    async def post(self, request):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        username = request.data['username']
        status = request.data['status']
        if not username or not status:
            return JsonResponse(
                {"message": "Username and status are required"},
                status = status.HTTP_400_BAD_REQUEST
            )
        friendshiprequest = FriendRequest.objects.get()
        friendshiprequest.delete()
        async with clients_lock:
            channel_name = connected_clients[username]
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            channel_name,
            {
                "type": "handle_friendship_request",
                "from": user.username,
                "status": status
            }
        )

        return JsonResponse(
            {"message": "Friend Request sent successfully"},
            status = status.HTTP_200_OK
        )