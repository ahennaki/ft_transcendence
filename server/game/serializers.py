from rest_framework             import serializers
from .models                    import Match, Setting
from prfl.serializers           import ProfileSerializer
from .models                    import MatchHistory

class MatchSerializer(serializers.ModelSerializer):
    player1 = ProfileSerializer()
    player2 = ProfileSerializer()

    class Meta:
        model = Match
        fields = ['player1', 'player2', 'start_time', 'status']

class MatchHistorySerializer(serializers.ModelSerializer):
    winner = ProfileSerializer()
    loser = ProfileSerializer()
    match = MatchSerializer()

    class Meta:
        model = MatchHistory
        fields = ['match', 'winner', 'loser', 'winner_score', 'loser_score', 'ended_at']

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ['mapname', 'ballcolor', 'score', 'botlevel', 'profile']
