from rest_framework import generics, status
from ..utils import Authenticate, print_green, print_red
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django_otp.plugins.otp_totp.models import TOTPDevice
from prfl.models import Profile

User = get_user_model()

class DeleteAccountView(generics.GenericAPIView):
    def post(self, request):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        # 6 digit code
        TOTPDevice.objects.filter(user=user).delete()
        user.delete()
        return JsonResponse(
            {"message": "User account and related data deleted successfully."},
            status=status.HTTP_200_OK
        )
            