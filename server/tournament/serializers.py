from rest_framework     import serializers
from .models            import Tournament, TournamentParticipant, Match
from django.db          import transaction
from prfl.serializers   import ProfileSerializer

class TournamentParticipantSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(source='user', read_only=True)

    class Meta:
        model = TournamentParticipant
        fields = ['id', 'profile', 'alias', 'joined_at']

class TournamentSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.user.username', read_only=True)
    participants = TournamentParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'created_by', 'status', 'created_at', 'updated_at', 'participants']

class TournamentNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'name']

class TournamentNameCheckSerializer(serializers.Serializer):
    tournament_name = serializers.CharField(max_length=255)

    def validate_tournament_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Tournament name cannot be empty or whitespace.")
        return value

    def validate(self, attrs):
        tournament_name = attrs.get('tournament_name')
        exists = Tournament.objects.filter(name__iexact=tournament_name).exists()
        attrs['name_taken'] = exists
        return attrs

class AliasCheckSerializer(serializers.Serializer):
    tournament_name = serializers.CharField(max_length=255)
    alias = serializers.CharField(max_length=255)

    def validate_tournament_name(self, value):
        if not Tournament.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Tournament with this name does not exist.")
        return value

    def validate(self, attrs):
        tournament_name = attrs.get('tournament_name')
        alias = attrs.get('alias')

        try:
            tournament = Tournament.objects.get(name__iexact=tournament_name)
        except Tournament.DoesNotExist:
            raise serializers.ValidationError({"tournament_name": "Tournament with this name does not exist."})

        if TournamentParticipant.objects.filter(tournament=tournament, alias__iexact=alias).exists():
            attrs['alias_taken'] = True
        else:
            attrs['alias_taken'] = False

        return attrs

class TournamentCreateSerializer(serializers.Serializer):
    tournament_name = serializers.CharField(max_length=255)
    alias = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_tournament_name(self, value):
        if Tournament.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Tournament with this name already exists.")
        return value

    def create(self, validated_data):
        user_profile = self.context['user'].profile
        tournament_name = validated_data['tournament_name']
        alias = validated_data.get('alias', f"{user_profile.user.username}'s Tournament")

        with transaction.atomic():
            tournament = Tournament.objects.create(
                name=tournament_name,
                created_by=user_profile,
                status='upcoming',
            )

            TournamentParticipant.objects.create(
                tournament=tournament,
                user=user_profile,
                alias=alias
            )

        return tournament

class TournamentJoinSerializer(serializers.Serializer):
    tournament_name = serializers.CharField(max_length=255)
    alias = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_tournament_name(self, value):
        if not Tournament.objects.filter(name__iexact=value, status='upcoming').exists():
            raise serializers.ValidationError("Upcoming tournament with this name does not exist.")
        return value

    def validate(self, attrs):
        tournament_name = attrs.get('tournament_name')
        alias = attrs.get('alias')
        user_profile = self.context['user'].profile

        try:
            tournament = Tournament.objects.get(name__iexact=tournament_name, status='upcoming')
        except Tournament.DoesNotExist:
            raise serializers.ValidationError({"tournament_name": "Upcoming tournament with this name does not exist."})

        if TournamentParticipant.objects.filter(tournament=tournament, user=user_profile).exists():
            raise serializers.ValidationError({"detail": "You are already a participant in this tournament."})

        if tournament.participants.count() >= 8:
            raise serializers.ValidationError({"detail": "Tournament has reached maximum participants."})

        if TournamentParticipant.objects.filter(tournament=tournament, alias__iexact=alias).exists():
            raise serializers.ValidationError({"alias": "Alias already taken in this tournament."})

        attrs['tournament'] = tournament
        attrs['user'] = user_profile
        return attrs

    def create(self, validated_data):
        tournament = validated_data['tournament']
        user_profile = validated_data['user']
        alias = validated_data.get('alias', f"{user_profile.user.username}")

        with transaction.atomic():
            participant = TournamentParticipant.objects.create(
                tournament=tournament,
                user=user_profile,
                alias=alias
            )

            if tournament.participants.count() == 8:
                tournament.status = 'ongoing'
                tournament.save()
                from .utils import create_initial_matches
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
