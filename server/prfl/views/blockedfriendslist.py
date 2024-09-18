from rest_framework             import generics, status
from django.http                import JsonResponse
from authentication.utils       import Authenticate
from ..models                   import BlockedFriend

class BlockedFriendsView(generics.GenericAPIView):
    def get(self, request):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        profile = user.profile
        blockedfriends = BlockedFriend.objects.filter(blocker=profile)

        blockedfriends_data = blockedfriends.values(
            'blocked_friend__username', 
            'blocked_friend__is_online', 
            'blocked_friend__picture', 
            'blocked_friend__rank'
        )

        return JsonResponse({"blockedfriends": list(blockedfriends_data)}, status=status.HTTP_200_OK)
