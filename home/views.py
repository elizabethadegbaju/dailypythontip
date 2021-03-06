import tweepy
from decouple import config
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector, SearchQuery, \
    SearchRank, TrigramSimilarity
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from home.models import Tip, Tag, TwitterUser
from home.serializers import TipSerializer


def index(request, template='home/tip_list.html',
          page_template='home/tip_list_page.html'):
    if request.is_ajax():
        template = page_template
    tips = Tip.objects.all().annotate(
        popularity=F('total_likes') + F('total_retweets')).order_by(
        '-popularity')
    tags = Tag.objects.all().order_by('name')
    return render(request, template,
                  {'tips': tips, 'page_template': page_template, 'tags': tags})


def filter_tag(request, tag, template='home/tip_list.html',
               page_template='home/tip_list_page.html'):
    if request.is_ajax():
        template = page_template
    vector = SearchVector('text')
    query = SearchQuery(tag)
    tips = Tip.objects.annotate(
        rank=SearchRank(vector, query)).filter(rank__gt=0).order_by(
        '-rank')
    tags = Tag.objects.all().order_by('name')
    return render(request, template,
                  {'tips': tips, 'page_template': page_template, 'tags': tags})


def search_tips(request, template='home/tip_list.html',
                page_template='home/tip_list_page.html'):
    if request.is_ajax():
        template = page_template
    if 'q' in request.GET:
        query = request.GET['q']
        vector = SearchVector('text') + SearchVector(
            'author_name') + SearchVector('author_email')
        tips = Tip.objects.annotate(
            rank=SearchRank(vector, SearchQuery(query)),
            similarity=TrigramSimilarity('text', query)).order_by('-rank')
    else:
        tips = Tip.objects.all()
    tags = Tag.objects.all().order_by('name')
    return render(request, template,
                  {'tips': tips, 'page_template': page_template, 'tags': tags})


def sort_tips(request, criteria, template='home/tip_list.html',
              page_template='home/tip_list_page.html'):
    if request.is_ajax():
        template = page_template
    tips = Tip.objects.all()
    if criteria == 'likes':
        sorted_tips = tips.order_by('-total_likes')
    elif criteria == 'retweets':
        sorted_tips = tips.order_by('-total_retweets')
    elif criteria == 'recent':
        sorted_tips = tips.order_by('-timestamp')
    else:
        sorted_tips = tips
    tags = Tag.objects.all().order_by('name')
    return render(request, template,
                  {'tips': sorted_tips, 'page_template': page_template,
                   'tags': tags})


def todays_tip(request):
    try:
        latest_tip = Tip.objects.latest()
        if latest_tip.timestamp.date() == now().date():
            tip = latest_tip
            return render(request, 'home/todays_tip.html', {'tip': tip})
        else:
            return render(request, 'home/todays_tip.html', {'tip': None})
    finally:
        return render(request, 'home/todays_tip.html', {'tip': None})


def log_in(request):
    if request.method == 'GET':
        return render(request, 'home/login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            auth = tweepy.OAuthHandler("CONSUMER_KEY", "CONSUMER_SECRET")
            auth.set_access_token(request.user.twitteruser.access_token,
                                  request.user.twitteruser.access_token_secret)
            api = tweepy.API(auth)

            # test authentication
            try:
                user = api.verify_credentials()
                if user is not None:
                    print("Authentication OK")
                else:
                    raise tweepy.TweepError
            except tweepy.TweepError:
                messages.error(request,
                               'Error connecting to your Twitter account')
                print("Error during authentication")
            return redirect('home:index')
        else:
            messages.error(request, 'Username or Password incorrect!')
            return render(request, 'home/login.html')


def create_account(request):
    if request.method == 'GET':
        return render(request, 'home/register.html')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = email.split('@')[0]
        user = User.objects.create_user(username=username, password=password,
                                        email=email, first_name=first_name,
                                        last_name=last_name)
        user.save()
        login(request, user)
        consumer_key = config('CONSUMER_KEY')
        consumer_secret = config('CONSUMER_SECRET')
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            logout(request)
            del_user(username)
            messages.error(request,
                           'Error connecting to your twitter account.')
            print('Error! Failed to get request token.')
            return render(request, 'home/register.html')

        request.session['request_token'] = auth.request_token['oauth_token']
        return redirect(redirect_url)


def del_user(username):
    user = User.objects.get(username=username)
    user.delete()


def log_out(request):
    logout(request)
    return redirect('home:index')


def link_twitter(request):
    consumer_key = config('CONSUMER_KEY')
    consumer_secret = config('CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    verifier = request.GET.get('oauth_verifier')
    token = request.session['request_token']
    del request.session['request_token']
    auth.request_token = {'oauth_token': token, 'oauth_token_secret': verifier}

    try:
        auth.get_access_token(verifier)
        api = tweepy.API(auth)
        username = api.me().screen_name
        access_token = auth.access_token
        access_token_secret = auth.access_token_secret
        twitter_user = TwitterUser.objects.create(
            access_token=access_token, user=request.user,
            access_token_secret=access_token_secret)
        twitter_user.user.username = username
        twitter_user.user.save()
        twitter_user.save()
        messages.success(request, 'Account created successfully!')
    except tweepy.TweepError:
        messages.error(request, 'Error connecting to your twitter account.')
        print('Error! Failed to get access token.')
        print(tweepy.TweepError)
    return redirect('home:index')


@login_required
def retweet(request, tweet_id):
    consumer_key = config('CONSUMER_KEY')
    consumer_secret = config('CONSUMER_SECRET')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    try:
        access_token = request.user.twitteruser.access_token
        access_token_secret = request.user.twitteruser.access_token_secret
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, retry_count=6)

        api.retweet(tweet_id)
        messages.success(request, 'Python tip retweeted successfully!')
    except tweepy.TweepError:
        messages.error(request, 'Sorry, I was unable to retweet that Python '
                                'Tip')
        print('Error! Unable to retweet Python Tip.')
    return redirect('home:index')


@api_view(('GET', 'POST'))
@renderer_classes((JSONRenderer,))
@csrf_exempt
def api_tip_list(request):
    """
    List all code tips, or create a new tip.
    """
    if request.method == 'GET':
        tips = Tip.objects.all()
        serializer = TipSerializer(tips, many=True)
        return Response(data=serializer.data)

    elif request.method == 'POST':
        if request.user.is_authenticated:
            data = JSONParser().parse(request)
            if len(data['text']) > 140:
                return Response(status=400, data={
                    'error': 'This tip is too long. Max length is 140 '
                             'characters.'})
            data['timestamp'] = now()
            serializer = TipSerializer(data=data)
            if serializer.is_valid():
                text = serializer.validated_data['text']
                similar_tips = Tip.objects.annotate(
                    similarity=TrigramSimilarity('text', text)).filter(
                    similarity__gte=0.5)
                if similar_tips.exists():
                    return Response(status=400, data={
                        'error': 'This tip is too similar to existing tips in the database'})
                else:
                    serializer.save()
                    return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        else:
            return Response(status=401, data={'error': 'login required'})


@api_view(('GET', 'PUT', 'DELETE'))
@csrf_exempt
@renderer_classes((JSONRenderer,))
def api_tip_detail(request, pk):
    """
    Retrieve, update or delete a python tip.
    """
    try:
        tip = Tip.objects.get(pk=pk)
    except Tip.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = TipSerializer(tip)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if request.user.is_authenticated:
            data = JSONParser().parse(request)
            if len(data['text']) > 140:
                return Response(status=400, data={
                    'error': 'This tip is too long. Max length is 140 '
                             'characters.'})
            data['timestamp'] = now()
            serializer = TipSerializer(tip, data=data)
            if serializer.is_valid():
                text = serializer.validated_data['text']
                similar_tips = Tip.objects.annotate(
                    similarity=TrigramSimilarity('text', text)).filter(
                    similarity__gte=0.5)
                if similar_tips.exists():
                    return Response(status=400, data={
                        'error': 'Updating this tip makes it too similar to existing tips in the database'})
                else:
                    serializer.save()
                    return Response(serializer.data)
            return Response(serializer.errors, status=400)
        else:
            return Response(status=401, data={'error': 'login required'})

    elif request.method == 'DELETE':
        if request.user.is_authenticated:
            tip.delete()
            return HttpResponse(status=204)
        else:
            return Response(status=401, data={'error': 'login required'})
