from rest_framework import serializers

from codes.models import Code


class CodeSerializer(serializers.Serializer):
    token_id = serializers.IntegerField()
    views = serializers.IntegerField(required=False)

    def create(self, validated_data):
        return Code.objects.create(**validated_data)

    class Meta:
        model = Code
        fields = ('id', 'tokenId')