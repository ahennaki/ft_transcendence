from rest_framework import serializers
from ..models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'username', 'picture', 'rank', 'badge', 'isSettings', 'isInviting', 'background_picture'
        )
