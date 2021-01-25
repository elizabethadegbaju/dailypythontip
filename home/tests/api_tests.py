import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


@pytest.mark.django_db
class TipListTests(APITestCase):
    fixtures = ['tips.json']

    def setUp(self):
        self.url = reverse('home:api-tip-list')
        self.user = User.objects.create(username='admin', password='1234')

    def test_load_tips(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_create_tip_login_error(self):
        data = {"author_name": "python_tip",
                "author_email": "pythontip@example.com",
                "text": "login error will happen"}
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_tip_similarity_check_error(self):
        self.client.force_login(user=self.user)
        data = {"author_name": "python_tip",
                "author_email": "pythontip@example.com",
                "text": "For people coming from #rstats:\n\n1) Do you miss dplyr? `siuba` is a Python port of dplyr with select, filter, mutate &amp; summarize over #pandas data frames.\n\nhttps://t.co/zBfeH6nEnQ\n\n2) RStudio 1.4 has new Python functions, incl. display of Python objects \n\nhttps://t.co/SgfVg64y4z https://t.co/tFpQID2cUE"}
        response = self.client.post(self.url, data, format='json')
        self.client.logout()
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_tip_success(self):
        self.client.force_login(user=self.user)
        data = {"author_name": "python_tip",
                "author_email": "pythontip@example.com",
                "text": "There is no other tip in the database that has text similar to this, I promise"}
        response = self.client.post(self.url, data, format='json')
        self.client.logout()
        assert response.status_code == status.HTTP_201_CREATED
