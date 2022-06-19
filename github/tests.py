from django.test import TestCase
from users.models import User
from unittest.mock import patch
from rest_framework.test import APIClient
import datetime
import os
import jwt


class MockResponse:

    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            'login': 'test_user'
        }

# Create your tests here.
class TestGithub(TestCase):

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

    @patch("requests.get", return_value=MockResponse())
    def test_githubAccessToken(self, mocked):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.post('/github/githubAccessToken', {'code': '123'})
        self.assertEqual(response.status_code, 200)

    @patch("requests.get", return_value=MockResponse())
    def test_githubUserRepos_no_token(self, mocked):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.get('/github/githubUserRepos')
        self.assertEqual(response.status_code, 404)

    @patch("requests.get", return_value=MockResponse())
    def test_githubUserRepos(self, mocked):
        user = User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D')
        user.githubToken = '123'
        user.save()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.get('/github/githubUserRepos')
        self.assertEqual(response.status_code, 200)

    @patch("requests.get", return_value=MockResponse())
    @patch("requests.post", return_value=MockResponse())
    def test_createRepo(self, mocked, moked2):
        user = User.objects.get(hash='0xC117aDa59a2244594B967eFB9eD43663BB3c7F6D')
        user.githubToken = '123'
        user.save()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.decode('utf-8'))
        response = client.get('/github/githubUserRepos')
        self.assertEqual(response.status_code, 200)
