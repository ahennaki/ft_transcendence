from rest_framework             import serializers
from .models                    import Match, Setting
from prfl.serializers           import ProfileSerializer
from .models                    import MatchHistory

class MatchSerializer(serializers.ModelSerializer):
    player1 = ProfileSerializer()
    player2 = ProfileSerializer()

    class Meta:
        model = Match
        fields = '__all__'
        extra_kwargs = {
            'player1': {'read_only': True},
            'player2': {'read_only': True},
            'start_time': {'read_only': True},
            'status': {'read_only': True},
        }

class MatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchHistory
        fields = ['match', 'winner', 'loser', 'winner_score', 'loser_score', 'ended_at']

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ['mapname', 'ballcolor', 'score', 'botlevel', 'profile']
