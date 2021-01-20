"""
Models for dailypythontip home app
"""
from django.db import models


class Tip(models.Model):
    """
    This represents a single Daily Python Tip
    """
    timestamp = models.DateTimeField()
    tip = models.TextField()
    link = models.BooleanField(default=False)
    author = models.CharField(max_length=255)
    published = models.TextField()
    total_likes = models.IntegerField()
    total_retweets = models.IntegerField()


class TipLink(models.Model):
    """
    This represents a single link in a Daily Python Tip
    """
    tip = models.ForeignKey(to=Tip, on_delete=models.CASCADE)
    link = models.TextField()
