from rest_framework         import generics, status
from django.http            import JsonResponse
from django.conf            import settings
from django.contrib.auth    import get_user_model
from ..utils                import decodeJWTToken, Authenticate, invalidatetoken
from django.core.cache      import cache
import hashlib

User = get_user_model()

class DeleteAccountAffected(generics.GenericAPIView):
    def get(self, request, token):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        tk = decodeJWTToken(token)
        if not tk:
            return JsonResponse(
                {"message": "Invalid token"},
                status = status.HTTP_400_BAD_REQUEST
            )
        user.delete()
        return invalidatetoken(request, 'User account and related data deleted successfully.')