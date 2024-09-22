from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from authentication.utils import Authenticate
from ..models import Profile

class UploadProfilePictureView(generics.GenericAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        profile = user.profile
        picture = request.FILES.get('picture')

        if picture:
            profile.picture = picture
            profile.save()
            return JsonResponse(
                {"message": "Profile picture updated", "picture_url": profile.picture.url},
                status=status.HTTP_200_OK
            )
        else:
            return JsonResponse(
                {"message": "No picture uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )
