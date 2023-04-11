from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from store.models import Collection
import json

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
class TestCreateCollection(APITestCase):
    # def setUp(self) -> None:
    #     self.user_admin = User.objects.create_user(username='test_user_admin',email='test_user_admin@mail.ru',is_staff=True)
    #     access_admin  = get_tokens_for_user(self.user_admin)['access']
    #     self.auth_admin = 'JWT {0}'.format(access_admin )
    #
    #     self.user = User.objects.create_user(username='test_user',email='test_user@mail.ru')
    #     access = get_tokens_for_user(self.user)['access']
    #     self.auth = 'JWT {0}'.format(access)
    def test_if_user_is_anonymous_return_401(self):
        data = {
            'title':'Beauty Products'
        }
        response = self.client.post('/store/collections/',data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
    def test_if_user_is_not_admin_returns_403(self):
        self.user = User.objects.create_user(username='test_user',email='test_user@mail.ru')
        access = get_tokens_for_user(self.user)['access']
        self.auth = 'JWT {0}'.format(access)

        data = {
            'title': 'Beauty Products123'
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.auth)
        response = self.client.post('/store/collections/', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_if_data_is_invalid_returns_400(self):
        self.user_admin = User.objects.create_user(username='test_user_admin',email='test_user_admin@mail.ru',is_staff=True)
        access_admin  = get_tokens_for_user(self.user_admin)['access']
        self.auth_admin = 'JWT {0}'.format(access_admin )
        data = {
            'title': ''
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin)
        response = self.client.post('/store/collections/', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
    def test_if_data_is_valid_returns_201(self):
        self.user_admin = User.objects.create_user(username='test_user_admin', email='test_user_admin@mail.ru',
                                                   is_staff=True)
        access_admin = get_tokens_for_user(self.user_admin)['access']
        self.auth_admin = 'JWT {0}'.format(access_admin)
        data = {
            'title': 'test'
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_admin)
        response = self.client.post('/store/collections/', data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

class TestRetrieveCollection(APITestCase):
    def test_if_collection_exists_return_200(self):
        collection = Collection.objects.create(title='Baking')
        response = self.client.get(f'/store/collections/{collection.id}/')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data,{'id': collection.id, 'title': collection.title})


