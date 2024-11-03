from rest_framework import serializers
from ..models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'username', 'picture', 'rank', 'badge', 'isSettings', 'isInviting', 'background_picture'
        )
