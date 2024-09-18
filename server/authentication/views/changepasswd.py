from rest_framework import generics, status
from django.http    import JsonResponse
from datetime       import datetime, timezone
from ..utils        import Authenticate   

class ChangePasswd(generics.GenericAPIView):
    def post(self, request):
        # add authentication
        old_password = request.data['old_password']
        new_password = request.data['new_password']

        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_400_BAD_REQUEST
            )
        if not (old_password and new_password):
            return JsonResponse(
                {"message": "Old password and new password are required"},
                status = status.HTTP_400_BAD_REQUEST
            )

        if user.check_password(old_password):
            user.set_password(new_password)
            user.token_last_change = datetime.now(timezone.utc) 
            user.save()
            # generate jwt tokens
            return JsonResponse(
                {"message": "Password changed successfully. Please log in again because we logged you out from all your sessions"},
                status = status.HTTP_200_OK
            )
        return JsonResponse(
            {"message": "Incorrect old password"},
            status = status.HTTP_400_BAD_REQUEST
        )
