from rest_framework         import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from django.http            import JsonResponse
from authentication.utils   import Authenticate
from ..models               import Profile
from ..utils                import generate_presigned_url
from ..serializers           import ProfileImageUploadSerializer

class ProfileImageUploadView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        profile = user.profile
        serializer = ProfileImageUploadSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'Image uploaded successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        