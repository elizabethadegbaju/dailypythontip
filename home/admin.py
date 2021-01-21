"""
Register dailypythontip home models with Django Admin
"""
from django.contrib import admin

from home.models import Tip, TipLink, Tag

admin.site.register(Tip)
admin.site.register(TipLink)
admin.site.register(Tag)
