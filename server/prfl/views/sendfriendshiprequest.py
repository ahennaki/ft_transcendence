from rest_framework                 import generics, status
from django.http                    import JsonResponse
from authentication.utils           import Authenticate
from channels.layers                import get_channel_layer
from asgiref.sync                   import async_to_sync
from ..models                       import FriendRequest, Profile
from ..utils.connections_manager    import connected_clients, clients_lock 

class SendFriendshipRequestView(generics.GenericAPIView):
    async def post(self, request):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        username = request.data.get('username')
        if not username:
            return JsonResponse(
                {"message": "Username is required"},
                status = status.HTTP_400_BAD_REQUEST
            )
        profile = Profile.objects.get(username=username)
        if not profile:
            return JsonResponse(
                {"message": "User does not exist"},
                status = status.HTTP_404_NOT_FOUND
            )
        FriendRequest.objects.create(from_user=user.profile,to_user=profile)
        async with clients_lock:
            channel_name = connected_clients[username]
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            channel_name,
            {
                "type": "send_friendship_request",
                "from": user.username,
            }
        )

        return JsonResponse(
            {"message": "Friend Request sent successfully"},
            status = status.HTTP_200_OK
        )