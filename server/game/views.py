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
from django.db                  import models
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

    def get(self, request):
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            return JsonResponse(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        settings = Setting.objects.filter(profile=profile)
        if settings.exists():
            serializer = self.serializer_class(settings, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        else:
            setting, created = Setting.objects.update_or_create(profile=profile)
            profile.isSettings = True
            profile.save()
            serializer = self.serializer_class(setting, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)

class ProfileIdDataView(generics.GenericAPIView):
    serializer_class = ProfileSerializer

    def get(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return JsonResponse(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(profile)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

class PlayerMatchHistoryView(generics.ListAPIView):
    serializer_class = MatchHistorySerializer
    # serialiser_class = Profil

    def get(self, request, username):
        try:
            profile = Profile.objects.get(username=username)

        except Profile.DoesNotExist:
            return JsonResponse(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        match_history = MatchHistory.objects.filter(
            models.Q(winner=profile) | models.Q(loser=profile)
        )
        if match_history.exists():
            serializer = self.serializer_class(match_history, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {'message': 'No match_history found for this profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
            