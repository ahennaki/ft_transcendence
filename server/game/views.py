from django.http                import JsonResponse
from rest_framework             import status
from .models                    import Match, MatchHistory, PlayerQueue
from django.utils               import timezone
from prfl.models                import Profile
from prfl.serializers           import ProfileSerializer
from authentication.utils       import Authenticate
from rest_framework             import generics, status
from .serializers               import MatchSerializer, SettingSerializer
from channels.layers            import get_channel_layer
from asgiref.sync               import async_to_sync, sync_to_async 
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

class EndMatchView(generics.GenericAPIView):
    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
            winner = request.data.get('winner')
            loser = request.data.get('loser')
            winner_score = request.data.get('winner_score')
            loser_score = request.data.get('loser_score')

            MatchHistory.objects.create(
                match=match,
                winner=winner,
                loser=loser,
                winner_score=winner_score,
                loser_score=loser_score,
                ended_at=timezone.now()
            )

            match.status = 'finished'
            match.save()

            return JsonResponse({'message': 'Match ended and saved.'}, status=status.HTTP_200_OK)
        except Match.DoesNotExist:
            return JsonResponse({'error': 'Match not found'}, status=status.HTTP_404_NOT_FOUND)

class SettingUpdateView(generics.GenericAPIView):
    serializer_class = SettingSerializer

    def post(self, request):
        profile_id = request.data.get('profile')
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return Response(
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

            return Response(
                {'message': message, 'setting': serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(
            {'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class ProfileSettingsView(generics.GenericAPIView):
    serializer_class = SettingSerializer

    def get(self, request, profile_id):
        try:
            profile = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        settings = Setting.objects.filter(profile=profile)
        if settings.exists():
            serializer = self.serializer_class(settings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'message': 'No settings found for this profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
            