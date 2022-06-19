from rest_framework import serializers
import secrets
from users.models import User


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    hash = serializers.CharField(max_length=42)
    nonce = serializers.CharField(max_length=100, required=False)
    name = serializers.CharField(max_length=100, required=False)
    username = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(max_length=100, required=False)
    description = serializers.CharField(max_length=1000, required=False)
    image = serializers.ImageField(required=False)
    githubToken = serializers.CharField(max_length=100, required=False)
    github = serializers.CharField(max_length=100, required=False)
    twitter = serializers.CharField(max_length=100, required=False)
    linkedin = serializers.CharField(max_length=100, required=False)
    website = serializers.CharField(max_length=100, required=False)

    def create(self, validated_data):
        validated_data['nonce'] = secrets.token_urlsafe()
        return User.objects.create(**validated_data)

    class Meta:
        model = User
        fields = ('id', 'hash', 'nonce', 'name', 'username', 'email', 'description', 'image', 'githubToken', 'github', 'twitter', 'linkedin', 'website')

class SimpleUserSerializer(serializers.Serializer):
    hash = serializers.CharField(max_length=42)
    username = serializers.CharField(max_length=100, required=False)
    nonce = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('hash', 'username', 'nonce')