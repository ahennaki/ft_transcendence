from rest_framework             import serializers
from .models                    import Match, Setting
from prfl.serializers           import ProfileSerializer

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

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ['profile', 'mapname', 'ballcolor', 'score', 'botlevel', 'issetting']

# class GameInvitationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GameInvitation
#         fields = ['id', 'sender', 'receiver', 'status', 'created_at']
