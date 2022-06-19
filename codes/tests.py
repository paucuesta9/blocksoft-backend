from django.test import TestCase
from rest_framework.test import APIClient
from .models import Code
from users.models import User
import datetime
import os
import jwt


# Create your tests here.
class CodesTest(TestCase):

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

    def test_get_codes_liked_by_user_empty(self):
        response = self.client.get('/codes?0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_codes_liked_by_user(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()

        response = self.client.get('/codes?liked_by=0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{'token_id': 1, 'views': 0}])

    def test_get_codes_sort_by_views(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()

        code = Code.objects.create(
            token_id=2,
            views=1,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()

        response = self.client.get('/codes?sort=viewed')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{'token_id': 2, 'views': 1}, {'token_id': 1, 'views': 0}])

    def test_get_codes_sort_by_liked(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()

        Code.objects.create(
            token_id=2,
            views=1,
        )
        code = Code.objects.get(token_id=2)
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.liked_by.add(User.objects.get(hash='0x1234567890123456789012345678901234567890'))
        code.save()

        codes = Code.objects.all()

        response = self.client.get('/codes?sort=liked')
        self.assertEqual(response.status_code, 200)

    def test_get_codes_sort_error(self):
        response = self.client.get('/codes?sort=error')
        self.assertEqual(response.status_code, 400)

    def test_get_all(self):
        response = self.client.get('/codes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_get_all_with_codes(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()
        response = self.client.get('/codes')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{'token_id': 1, 'views': 0}])

    def test_create_code(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.post('/codes', {'token_id': 1, 'views': 0})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'token_id': 1, 'views': 0})

    def test_get_one_and_increases_views(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()
        response = self.client.get('/codes/1')
        self.assertEqual(response.status_code, 200)
        code = Code.objects.get(token_id=1)
        self.assertEqual(code.views, 1)

    def test_get_one_not_found_creates(self):
        response = self.client.get('/codes/1')
        self.assertEqual(response.status_code, 201)

    def test_get_likes_code(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()
        response = self.client.get('/codes/like/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'liked': 1})

    def test_get_likes_code_not_found(self):
        response = self.client.get('/codes/like/1')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"error": "Code does not exist"})

    def test_post_like_code_exists(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.save()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.post('/codes/like/1')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'success': True})

    def test_post_like_code_not_exists(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.post('/codes/like/1')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, {'success': True})

    def test_post_like_code_already_liked(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.post('/codes/like/1')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data, {"error": "Already liked"})

    def test_post_unlike_code_exists(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.liked_by.add(User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D'))
        code.save()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.delete('/codes/like/1')
        self.assertEqual(response.status_code, 200)

    def test_post_unlike_code_not_exists(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.delete('/codes/like/1')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {"error": "Code does not exist"})

    def test_post_unlike_code_not_liked(self):
        code = Code.objects.create(
            token_id=1,
            views=0,
        )
        code.save()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.delete('/codes/like/1')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data, {"error": "Not liked"})

