from rest_framework             import generics, status
from django.http                import JsonResponse
from authentication.utils       import Authenticate
from ..models                   import Friend

class SearchFriendsView(generics.GenericAPIView):
    def post(self, request):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        prefix = request.data.get('prefix')
        limit = int(request.GET.get('limit', 10))
        if not prefix:
            friends = Friend.objects.all()
        else:
            friends = Friend.objects.filter(username__icontains=prefix)

        friends_list = friends[:limit]
        friends_data = friends_list.values(
            'username', 
            'is_online', 
            'picture', 
            'rank'
        )
        return JsonResponse(
            {"friends": list(friends_data)},
            status=status.HTTP_200_OK
        )