"""
Register dailypythontip home models with Django Admin
"""
from django.contrib import admin

from home.models import Tip, TipLink

admin.site.register(Tip)
admin.site.register(TipLink)
