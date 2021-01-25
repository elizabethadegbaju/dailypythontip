import pytest
from django.contrib.auth.models import User
from django.db.models import Max
from django.test import TestCase
from django.urls import reverse

from home.models import TwitterUser


class TipTestCase(TestCase):
    fixtures = ['tips.json']

    def test_home_loads_properly(self):
        """The home page loads properly"""
        response = self.client.get(reverse('home:index'))
        assert response.status_code == 200

    def test_sort_tips_recent(self):
        response = self.client.get(
            reverse('home:sort-tips', kwargs={'criteria': 'recent'}))
        assert response.status_code == 200

    def test_sort_tips_retweets(self):
        response = self.client.get(
            reverse('home:sort-tips', kwargs={'criteria': 'retweets'}))
        tips = response.context['tips']
        total_retweets = tips.first().total_retweets
        tips = tips.aggregate(Max('total_retweets'))
        assert total_retweets == tips['total_retweets__max']
        assert response.status_code == 200

    def test_sort_tips_likes(self):
        response = self.client.get(
            reverse('home:sort-tips', kwargs={'criteria': 'likes'}))
        tips = response.context['tips']
        total_likes = tips.first().total_likes
        tips = tips.aggregate(Max('total_likes'))
        assert total_likes == tips['total_likes__max']
        assert response.status_code == 200

    def test_retrieve_todays_tip(self):
        response = self.client.get(reverse('home:retrieve-today'))
        tip = response.context['tip']
        assert tip is None

    def test_search_tips(self):
        response = self.client.get(reverse('home:search-tips'),
                                   {'q': '100daysofcode'})
        assert response.status_code == 200

    def test_filter_tips(self):
        response = self.client.get(
            reverse('home:filter-tag', kwargs={'tag': '100daysofcode'}))
        assert response.status_code == 200


@pytest.mark.django_db
class LoginTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='johndoe@example.com',
                                             password='passy',
                                             username='johnny')
        self.twitter_user = TwitterUser.objects.create(user=self.user,
                                                       access_token='12345abcde',
                                                       access_token_secret='abcdefg1234567')

    def test_login_fail(self):
        response = self.client.post(reverse('home:login'),
                                    {'username': 'admin',
                                     'password': '1234'}, follow=True)
        message = list(response.context['messages'])[0]
        assert message.tags == 'error'
        assert str(message) == 'Username or Password incorrect!'

    def test_login_success_twitter_fail(self):
        response = self.client.post(reverse('home:login'),
                                    {'username': 'johnny',
                                     'password': 'passy'}, follow=True)
        message = list(response.context['messages'])[0]
        assert message.tags == 'error'
        assert str(message) == 'Error connecting to your Twitter account'

    def test_logout(self):
        self.client.login(username='johnny', password='passy')
        response = self.client.post(reverse('home:logout'), follow=True)
        assert response.status_code == 200

    def tearDown(self):
        self.client.logout()


@pytest.mark.django_db
class RegisterTestCase(TestCase):
    def test_signup(self):
        response = self.client.post(reverse('home:register'),
                                    {'first_name': 'John', 'last_name': 'Doe',
                                     'email': 'johndoe@example.com',
                                     'password': 'passy'})
        assert response.status_code == 302
        assert 'https://api.twitter.com/oauth/authorize' in response.url

    def test_link_twitter(self):
        session = self.client.session
        session['request_token'] = 'qwerty09876543'
        session.save()
        response = self.client.get(reverse('home:link-twitter'),
                                   {'oauth_verifier': '1234abcde'},
                                   follow=True)
        message = list(response.context['messages'])[0]
        assert message.tags == 'error'
        assert str(message) == 'Error connecting to your twitter account.'


@pytest.mark.django_db
class RetweetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='johndoe@example.com',
                                             password='passy',
                                             username='johnny')
        self.twitter_user = TwitterUser.objects.create(user=self.user,
                                                       access_token='12345abcde',
                                                       access_token_secret='abcdefg1234567')

    def test_retweet(self):
        self.client.login(username='johnny', password='passy')
        response = self.client.get(reverse('home:retweet', kwargs={
            'tweet_id': 1352565704827039744}), follow=True)
        message = list(response.context['messages'])[0]
        assert message.tags == 'error'
        assert str(message) == 'Sorry, I was unable to retweet that Python Tip'
