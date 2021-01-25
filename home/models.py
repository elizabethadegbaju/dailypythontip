"""
Models for dailypythontip home app
"""
from django.contrib.auth.models import User
from django.db import models


class Tip(models.Model):
    """
    This represents a single Daily Python Tip
    """
    tweet_id = models.PositiveBigIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField()
    text = models.TextField()
    has_link = models.BooleanField(default=False)
    author_name = models.CharField(max_length=255)
    author_email = models.EmailField()
    published = models.BooleanField(default=False)
    total_likes = models.IntegerField(null=True, blank=True)
    total_retweets = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.author_name} - {self.text[:150]}...'

    class Meta:
        get_latest_by = 'timestamp'


class TipLink(models.Model):
    """
    This represents a single link in a Daily Python Tip
    """
    tip = models.ForeignKey(to=Tip, on_delete=models.CASCADE)
    link = models.TextField()

    def __str__(self):
        return f'({self.link}) {self.tip}'


class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class TwitterUser(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    access_token = models.TextField()
    access_token_secret = models.TextField()

    def __str__(self):
        return self.user.username
