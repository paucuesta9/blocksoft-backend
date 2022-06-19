from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

from users.models import User
from codes.models import Code
from codes.serializer import CodeSerializer
from users.serializer import UserSerializer, SimpleUserSerializer
from web3 import Web3
from hexbytes import HexBytes
from eth_account.messages import encode_defunct
from dotenv import load_dotenv
from api.permission import TokenAuth
import os
import jwt
import random
import string
import datetime

load_dotenv()

@api_view(['GET'])
def get_image(request, hash):
    try:
        user = User.objects.get(hash=hash)
        if user.image and user.image != '':
            image = open(user.image.path, 'rb').read()
            ext = user.image.path.split('.')[-1]
            mime = 'image/{}'.format(ext)
            return HttpResponse(image, content_type=mime)
        else:
            image = open(os.path.join(os.path.dirname(__file__), '../images/placeholder.jpg'), 'rb').read()
            return HttpResponse(image, content_type="image/jpeg")
    except User.DoesNotExist:
            image = open(os.path.join(os.path.dirname(__file__), '../images/placeholder.jpg'), 'rb').read()
            return HttpResponse(image, content_type="image/jpeg")

class UsersList(APIView):
    permission_classes = (TokenAuth,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        if request.GET.get('query'):
            try:
                users = User.objects.filter(hash__contains=request.GET['query']) | User.objects.filter(username__contains=request.GET['query']) | User.objects.filter(name__contains=request.GET['query'])
                serializer = SimpleUserSerializer(users, many=True)
                return Response(serializer.data, status=200)
            except User.DoesNotExist:
                return Response({'message': 'User not found'}, status=404)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class UserDetail(APIView):
    serializer_class = UserSerializer
    permission_classes = (TokenAuth,)


    def get(self, request, hash):
        try:
            user = User.objects.get(hash=hash)
            serializer = UserSerializer(user)
            codes = Code.objects.filter(liked_by__hash=user.hash)
            serializer_codes = CodeSerializer(codes, many=True)
            return Response({
                'publicAddress': serializer.data['hash'],
                'name': serializer.data['name'],
                'username': serializer.data['username'],
                'email': serializer.data['email'],
                'description': serializer.data['description'],
                'github': serializer.data['github'],
                'linkedin': serializer.data['linkedin'],
                'website': serializer.data['website'],
                'twitter': serializer.data['twitter'],
                "liked": serializer_codes.data
            }, status=200)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=404)

    def put(self, request, hash, format=None):
        try:
            if request.user.hash == hash:
                user = User.objects.get(hash=hash)
                for key, value in request.data.items():
                    if not hasattr(user, key):
                        return Response({"error": "Key does not exist"}, status=400)
                    setattr(user, key, value)
                user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data, status=200)
            else:
                return Response({"error": "Can't modify other profile"}, status=403)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=404)

class UserAuth(APIView):
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        if request.GET.get('publicAddress'):
            try:
                user = User.objects.get(hash=request.GET['publicAddress'])
                serializer = UserSerializer(user)
                return Response({'publicAddress': serializer.data['hash'], 'nonce': serializer.data['nonce']}, status=200)
            except User.DoesNotExist:
                serializer = UserSerializer(data={'hash': request.GET['publicAddress']})
                print(serializer.is_valid())
                if serializer.is_valid():
                    serializer.save()
                    return Response({'publicAddress': serializer.data['hash'], 'nonce': serializer.data['nonce']}, status=201)
                return Response(serializer.errors, status=400)
        else:
            return Response({"error": "publicAddress is required"}, status=400)

    def post(self, request, format=None):
        try:
            user = User.objects.get(hash=request.data['publicAddress'])
            serializer = UserSerializer(user)
            w3 = Web3(Web3.HTTPProvider(""))
            message = encode_defunct(text=serializer.data['nonce'])
            address = w3.eth.account.recover_message(message, signature=HexBytes(
                request.data['signature']))
            print(address)
            if address.lower() == serializer.data['hash'].lower():
                payload = {'publicAddress': serializer.data['hash'],"exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=6)}
                token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')
                user.nonce = ''.join(random.choices(string.ascii_lowercase, k=100))
                user.save()
                return Response({"success": "Signature is valid", "token": token, "githubToken": user.githubToken is not None}, status=200)
            else:
                return Response({"error": "Signature is not valid"}, status=400)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=404)