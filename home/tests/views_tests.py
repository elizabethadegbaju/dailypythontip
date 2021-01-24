import pytest
from django.test import TestCase


class TipTestCase(TestCase):
    def test_home_loads_properly(self):
        """The home page loads properly"""
        response = self.client.get('/')
        assert response.status_code == 200


class AuthenticationTestCase(TestCase):
    def test_login_loads_properly(self):
        """The login page loads properly"""
        response = self.client.get('/login/')
        assert response.status_code == 200
