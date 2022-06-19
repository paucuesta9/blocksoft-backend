from attr import fields
from django.contrib.auth import get_user_model
from rest_framework import serializers


class LanguageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)

    class Meta:
        model = get_user_model()
        fields = ('name')
