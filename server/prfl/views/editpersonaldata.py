from rest_framework             import generics, status
from django.http                import JsonResponse
from authentication.utils       import Authenticate

class EditPersonalDataView(generics.GenericAPIView):
    def post(self, request):
        user = Authenticate(request)
        if not user.is_authenticated:
            return JsonResponse(
                {"message": "User is not authenticated"},
                status = status.HTTP_401_UNAUTHORIZED
            )
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        phone_number = request.data.get('phone_number')
        profile = user.profile
        if first_name:
            profile.first_name = first_name
            profile.save()
        if last_name:
            profile.last_name = last_name
            profile.save()
        if phone_number:
            profile.phone_number = phone_number
            profile.save()
        return JsonResponse(
            {"message": "Personal data updated successfully"},
            status = status.HTTP_200_OK
        )