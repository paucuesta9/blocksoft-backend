from rest_framework.permissions import BasePermission
import jwt
from dotenv import load_dotenv
import os
from users.models import User
from users.serializer import UserSerializer

load_dotenv()

class TokenAuth(BasePermission):
    serializer_class = UserSerializer

    def has_permission(self, request, view):
        # check if request is /users or contains /users/
        if request.method == 'GET' and 'github' not in request.path:
            return True
        token = request.META.get('HTTP_AUTHORIZATION')
        if request.method != 'GET' and token is None:
            return False
        try:
            token = token.split(' ')[1]
            payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            user = User.objects.get(hash=payload['publicAddress'])
            request.user = user
        except jwt.ExpiredSignatureError:
            self.message = {'error': 'Token expired', 'code': 1}
            return False
        except User.DoesNotExist:
            return False
        return True