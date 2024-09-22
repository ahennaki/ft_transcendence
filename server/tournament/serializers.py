from rest_framework 		import serializers
from .models 				import Tournament, TournamentParticipant, Match
from authentication.models 	import CustomUser
from .utils 				import create_initial_matches

class TournamentSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'description', 'created_by', 'status', 'created_at', 'updated_at']

class TournamentCreateSerializer(serializers.Serializer):
    tournamentName = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1024, required=False, allow_blank=True)

    def validate_tournamentName(self, value):
        if Tournament.objects.filter(name=value).exists():
            raise serializers.ValidationError("Tournament with this name already exists.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        tournament_name = validated_data['tournamentName']
        description = validated_data.get('description', '')

        tournament = Tournament.objects.create(
            name=tournament_name,
            description=description,
            created_by=user,
            status='upcoming',
        )

        TournamentParticipant.objects.create(
            tournament=tournament,
            user=user
        )

        return tournament

class TournamentJoinSerializer(serializers.Serializer):
    tournamentName = serializers.CharField(max_length=255)

    def validate_tournamentName(self, value):
        try:
            tournament = Tournament.objects.get(name=value)
        except Tournament.DoesNotExist:
            raise serializers.ValidationError("Tournament with this name does not exist.")
        return value

    def validate(self, attrs):
        tournament_name = attrs.get('tournamentName')
        user = self.context['request'].user

        try:
            tournament = Tournament.objects.get(name=tournament_name)
        except Tournament.DoesNotExist:
            raise serializers.ValidationError({"tournamentName": "Tournament with this name does not exist."})

        if tournament.status != 'upcoming':
            raise serializers.ValidationError({"tournamentName": "Tournament is not open for joining."})

        if TournamentParticipant.objects.filter(tournament=tournament, user=user).exists():
            raise serializers.ValidationError({"detail": "You are already a participant in this tournament."})

        if tournament.participants.count() >= 8:
            raise serializers.ValidationError({"detail": "Tournament has reached maximum participants."})

        attrs['tournament'] = tournament
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        tournament = validated_data['tournament']
        user = validated_data['user']

        participant = TournamentParticipant.objects.create(
            tournament=tournament,
            user=user
        )

        if tournament.participants.count() == 8:
            tournament.status = 'ongoing'
            tournament.save()
            create_initial_matches(tournament)

        return participant

class MatchUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['winner', 'score_player1', 'score_player2', 'completed']

    def validate(self, attrs):
        if attrs.get('completed') and not attrs.get('winner'):
            raise serializers.ValidationError("Winner must be specified if the match is completed.")
        return attrs
