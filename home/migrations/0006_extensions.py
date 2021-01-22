from django.contrib.postgres.operations import TrigramExtension, \
    UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0005_auto_20210122_2047'),
    ]
    operations = [
        TrigramExtension(),
        UnaccentExtension(),
    ]
