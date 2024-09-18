from rest_framework             import generics, status
from django.http                import JsonResponse
from authentication.utils       import Authenticate
from ..models                   import Friend

class FriendsListView(generics.GenericAPIView):
    def get(self, request):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        profile = user.profile
        friends = Friend.objects.filter(profile=profile)

        friends_data = friends.values(
            'friend__username', 
            'friend__is_online', 
            'friend__picture', 
            'friend__rank'
        )
        return JsonResponse(
            {"friends": list(friends_data)},
            status = status.HTTP_200_OK,
        )
