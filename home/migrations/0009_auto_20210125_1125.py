# Generated by Django 3.1.5 on 2021-01-25 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20210125_1035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tip',
            name='total_likes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tip',
            name='total_retweets',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tip',
            name='tweet_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
