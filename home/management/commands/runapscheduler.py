import logging

import tweepy
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from decouple import config
from django.conf import settings
from django.core.management import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from home.models import Tag, Tip, TipLink

logger = logging.getLogger(__name__)


def retrieve_nested_url(urls):
    links = list()
    while urls:
        mapping = urls.pop()
        try:
            items = mapping.items()
        except AttributeError:
            continue

        for key, value in items:
            if key == 'url':
                links.append(value)
            else:
                urls.append(value)
    return links


def fetch_tweets():
    """
    Retrieve tweets from @python_tip account

    :param request:
    """
    consumer_key = config('CONSUMER_KEY')
    consumer_secret = config('CONSUMER_SECRET')
    access_token = config('ACCESS_TOKEN')
    access_token_secret = config('ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, retry_count=6)

    tweets = tweepy.Cursor(api.user_timeline, id='python_tip',
                           tweet_mode='extended').items()
    for tweet in tweets:
        create_tip(tweet)


def create_tip(tweet):
    """
    Format a single tweet and extract fields for Tip and TipLink model

    :param tweet:
    """
    if 'hashtags' in tweet.entities:
        for hashtag in tweet.entities['hashtags']:
            tag, created = Tag.objects.get_or_create(
                name=hashtag['text'].lower())
            if created:
                tag.save()
    try:
        text = tweet.retweeted_status.full_text
    except AttributeError:
        text = tweet.full_text
    tip, created = Tip.objects.update_or_create(tweet_id=tweet.id,
                                                defaults={'text': text,
                                                          'published': True,
                                                          'author': tweet.author.screen_name,
                                                          'total_likes': str(
                                                              tweet.favorite_count),
                                                          'total_retweets': str(
                                                              tweet.retweet_count),
                                                          'timestamp': tweet.created_at})

    if created:
        tip.save()
        if tweet.entities['urls']:
            tip.has_link = True
            tip.save()
            links = retrieve_nested_url(tweet.entities['urls'])
            print(links)
            for link in links:
                tip_link = TipLink.objects.create(tip=tip, link=link)
                tip_link.save()


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age`
    from the database. """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler"

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(fetch_tweets, trigger=CronTrigger(day='*/1'),
                          id="fetch_tweets", max_instances=1,
                          replace_existing=True)
        logger.info("Added job 'fetch_tweets'.")

        scheduler.add_job(delete_old_job_executions,
                          trigger=CronTrigger(day_of_week="mon", hour="00",
                                              minute="00"),
                          id="delete_old_job_executions", max_instances=1,
                          replace_existing=True)
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
