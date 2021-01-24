"""
Register dailypythontip home models with Django Admin
"""
from django.contrib import admin

from home.models import Tip, TipLink, Tag, TwitterUser

admin.site.register(Tip)
admin.site.register(TipLink)
admin.site.register(Tag)
admin.site.register(TwitterUser)
