from rest_framework             import generics, status
from django.http                import JsonResponse
from authentication.utils       import Authenticate
from ..models                   import Profile

class SearchProfilesView(generics.GenericAPIView):
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
            profiles = Profile.objects.all()
        else:
            profiles = Profile.objects.filter(username__icontains=prefix)

        profiles_list = profiles[:limit]
        profiles_data = profiles_list.values(
            'username', 
            'is_online', 
            'picture', 
            'rank'
        )
        return JsonResponse(
            {"profiles": list(profiles_data)},
            status=status.HTTP_200_OK
        )