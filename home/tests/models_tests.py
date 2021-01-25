import pytest
from django.test import TestCase
from django.utils.timezone import now

from ..models import *

pytestmark = pytest.mark.django_db


class TipTestCase(TestCase):
    def setUp(self):
        """Set up test data for testing Tip model"""
        self.tip = Tip.objects.create(timestamp=now(),
                                      tweet_id=827622022461214722,
                                      text='This is not a real python tip. '
                                           'It is only for testing '
                                           'purposes',
                                      author_name='python_tip',
                                      author_email='pythontip@example.com',
                                      published=True, total_retweets=150,
                                      total_likes=500)

    def test_tip_has_links(self):
        """Links are correctly set on Tips"""
        assert self.tip.has_link is False
        self.tip.has_link = True
        TipLink.objects.create(link="https://www.google.com/",
                               tip=self.tip)
        assert self.tip.has_link is True
        assert self.tip.tiplink_set.count() == 1

    def test_tip_object_parsing(self):
        """Tip object parses to string properly"""
        assert str(
            self.tip) == f'{self.tip.author_name} - {self.tip.text[:150]}...'


class TagTestCase(TestCase):
    def setUp(self):
        """Set up test data for testing Comment model"""
        self.tag = Tag.objects.create(name='tagger')

    def test_tag_object_parsing(self):
        assert str(self.tag) == self.tag.name


class TipLinkTestCase(TestCase):
    def setUp(self):
        """Set up test data for testing Tip model"""
        tip = Tip.objects.create(timestamp=now(),
                                 tweet_id=827622022461214722,
                                 text='This is not a real python tip. '
                                      'It is only for testing '
                                      'purposes', author_name='python_tip',
                                 author_email='pythontip@example.com',
                                 published=True, total_retweets=150,
                                 total_likes=500)
        self.tip_link = TipLink.objects.create(tip=tip,
                                               link='https://www.google.com/')

    def test_tip_link_object_parsing(self):
        assert str(
            self.tip_link) == f'({self.tip_link.link}) {self.tip_link.tip}'


class TwitterUserTestCase(TestCase):
    def setUp(self):
        """Set up test data for testing TwitterUser model"""
        user = User.objects.create_user(username='johnny', password='passy',
                                        email='johndoe@example.com')
        self.twitter_user = TwitterUser.objects.create(user=user,
                                                       access_token='12345abcde',
                                                       access_token_secret='abcdef123456')

    def test_twitter_user_object_parsing(self):
        assert str(self.twitter_user) == self.twitter_user.user.username
