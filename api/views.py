from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.models import Language
from api.serializer import LanguageSerializer

@api_view(['GET'])
def get_languages(request):
    try:
        languages = Language.objects.all().order_by('name')
        serializer = LanguageSerializer(languages, many=True)
        return Response(serializer.data, status=200)
    except Language.DoesNotExist:
        return Response(status=404)