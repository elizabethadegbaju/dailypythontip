from rest_framework import serializers

from .models import Tip


class TipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tip
        fields = ['timestamp', 'author_name', 'author_email', 'text']
