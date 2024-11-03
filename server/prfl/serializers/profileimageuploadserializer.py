from rest_framework import serializers
from ..models       import Profile

class ProfileImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['picture', 'background_picture']
        