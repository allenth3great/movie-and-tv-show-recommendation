from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class MovieSearchTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_search_movies(self):
        response = self.client.get(reverse('movie-search'), {'query': 'Inception'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)  

    def test_search_movies_no_query(self):
        response = self.client.get(reverse('movie-search'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
