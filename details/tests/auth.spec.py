import json
import jwt
import datetime
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from ..models import User, Organisation

class TestAuth(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login') 

        # Sample user data
        self.user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "securepassword",
            "phone": "+2347048581078"
        }

        # JWT Configuration
        self.secret_key = "secret" 
        self.algorithm = 'HS256'

    def create_jwt_token(self, user_id):
        payload = {
            'id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_jwt_token(self, token):
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

    def test_register_user_success(self):
        response = self.client.post(self.register_url, data=json.dumps(self.user_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Registration successful')
        self.assertIn('accessToken', data['data'])

        # Verify the default organisation
        user = User.objects.get(email=self.user_data['email'])
        org = Organisation.objects.filter(users=user).first()
        self.assertEqual(org.name, f"{self.user_data['firstName']}'s Organisation")

    def test_login_user_success(self):
        self.client.post(self.register_url, data=json.dumps(self.user_data), content_type='application/json')
        response = self.client.post(self.login_url, data=json.dumps({
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Login successful')
        self.assertIn('accessToken', data['data'])

    def test_register_missing_fields(self):
        incomplete_data = self.user_data.copy()
        del incomplete_data['firstName']
        response = self.client.post(self.register_url, data=json.dumps(incomplete_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        data = response.json()
        self.assertEqual(data['errors'][0]['field'], 'firstName')

    def test_register_duplicate_email(self):
        self.client.post(self.register_url, data=json.dumps(self.user_data), content_type='application/json')
        response = self.client.post(self.register_url, data=json.dumps(self.user_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        data = response.json()
        self.assertEqual(data['errors'][0]['field'], 'email')

    def test_token_expiry(self):
        user_id = 1  
        token = self.create_jwt_token(user_id)
        decoded_token = self.decode_jwt_token(token)
        self.assertIn('exp', decoded_token)

        expired_payload = {
            'id': user_id,
            'exp': datetime.datetime.utcnow() - datetime.timedelta(seconds=1),
            'iat': datetime.datetime.utcnow()
        }
        expired_token = jwt.encode(expired_payload, self.secret_key, algorithm=self.algorithm)
        
        with self.assertRaises(jwt.ExpiredSignatureError):
            self.decode_jwt_token(expired_token)

    def test_organisation_access_restriction(self):
        self.client.post(self.register_url, data=json.dumps(self.user_data), content_type='application/json')
        user2_data = self.user_data.copy()
        user2_data['email'] = 'jane.doe@example.com'
        user2_response = self.client.post(self.register_url, data=json.dumps(user2_data), content_type='application/json')
        print(user2_response.json())
        organisations_url = reverse('record', args=[user2_response.json()["data"]["user"]['userId']])
        details = self.client.get(organisations_url)
        self.assertEqual(details.status_code, status.HTTP_403_FORBIDDEN) 

