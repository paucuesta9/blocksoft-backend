import datetime

from django.test import TestCase
from rest_framework.test import APIClient
from .models import User
import datetime
import os
import jwt

# Create your tests here.
class TestUsers(TestCase):

    token = None

    def setUp(self):
        payload = {'publicAddress': '0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D',
                   "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=6)}
        self.token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')

        User.objects.create(
            hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D',
            nonce='qwertyuiopasdfghjklñzxcvbnm'
        )

        User.objects.create(
            hash='0x1234567890123456789012345678901234567890',
            nonce='qwertyuiopasdfghjklñzxcvbnm'
        )


    def test_users_list(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 404)

    def test_user_list_search(self):
        response = self.client.get('/users?query=1234567890123456789012345678901234567890')
        self.assertEqual(response.status_code, 200)

    def test_user_list_search_not_found(self):
        response = self.client.get('/users?query=123456789012345678901234567890123456798')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_user_create(self):
        # post with bearer
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.post('/users', {
            'hash': '0x1234567890123456789012345678901234567891'
        })
        self.assertEqual(response.status_code, 201)

    def test_user(self):
        response = self.client.get('/users/0x1234567890123456789012345678901234567890')
        self.assertEqual(response.status_code, 200)

    def test_user_update(self):
        # post with bearer
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.put('/users/0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D', {
            'name': 'test'
        })
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D')
        self.assertEqual(user.name, 'test')

    def test_user_get_nonce(self):
        response = self.client.get('/users/auth?publicAddress=0x1234567890123456789012345678901234567890')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nonce'], 'qwertyuiopasdfghjklñzxcvbnm')

    def test_get_user_image(self):
        response = self.client.get('/users/0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D/image')
        self.assertEqual(response.status_code, 200)

    # def test_user_auth(self):
    #     w3 = Web3(Web3.HTTPProvider(""))
    #     private_key = '0653862f6b91868eba732e2889cb5745653efcb75c417b560d15a98fc21d14af'
    #     message = User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D').nonce
    #     signature = w3.eth.account.signHash(w3.keccak(text=message), private_key)
    #
    #     response = self.client.post('/users/auth', {
    #         'publicAddress': '0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D',
    #         'signature': signature.signature.hex()
    #     })
    #
    #     self.assertEqual(response.status_code, 200)

