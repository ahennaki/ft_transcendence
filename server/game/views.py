from django.http                import JsonResponse
from rest_framework             import status
from .models                    import Match, MatchHistory, PlayerQueue, Setting
from django.utils               import timezone
from prfl.models                import Profile
from prfl.serializers           import ProfileSerializer
from authentication.utils       import Authenticate
from rest_framework             import generics, status
from .serializers               import MatchSerializer, SettingSerializer, MatchHistorySerializer
from channels.layers            import get_channel_layer
from asgiref.sync               import async_to_sync, sync_to_async 
from authentication.utils       import print_red, print_green, print_yellow
import time

class MatchStatusView(generics.GenericAPIView):
    serializer_class = MatchSerializer

    def get(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            serialized_match = self.serializer_class(match).data
            return JsonResponse(serialized_match, status=status.HTTP_200_OK)
        except Match.DoesNotExist:
            return JsonResponse({
                'error': 'Match not found'
                }, status=status.HTTP_404_NOT_FOUND)


class PlayerMatchHistoryView(generics.ListAPIView):
    serializer_class = MatchHistorySerializer

    def get(self, request, username):
        print_yellow(f"fitshing mach history from username: {username}")
        try:
            player_profile = Profile.objects.get(username=username)
        except Profile.DoesNotExist:
            return JsonResponse(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        return MatchHistory.objects.filter(
            models.Q(winner=player_profile) | models.Q(loser=player_profile)
        )
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        print_green(f'data: {response.data}')
        return response

class SettingUpdateView(generics.GenericAPIView):
    serializer_class = SettingSerializer

    def post(self, request):
        profile_id = request.data.get('profile')
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return JsonResponse(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            setting, created = Setting.objects.update_or_create(
                profile=profile,
                defaults=serializer.validated_data
            )
            profile.isSettings = True
            profile.save()
            message = "Setting created successfully." if created else "Setting updated successfully."

            return JsonResponse(
                {'message': message, 'setting': serializer.data},
                status=status.HTTP_200_OK
            )
        return JsonResponse(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class ProfileSettingsView(generics.GenericAPIView):
    serializer_class = SettingSerializer

    def get(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return JsonResponse(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        settings = Setting.objects.filter(profile=profile)
        if settings.exists():
            serializer = self.serializer_class(settings, many=True)
            print_yellow(f'data: {serializer.data}')
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {'message': 'No settings found for this profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
