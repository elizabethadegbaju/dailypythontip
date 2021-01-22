from django.contrib.postgres.search import SearchVector, SearchQuery, \
    SearchRank
from django.db.models import F
from django.shortcuts import render
from django.utils.timezone import now

from home.models import Tip, Tag


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
        query = SearchQuery(request.GET['q'])
        vector = SearchVector('text') + SearchVector('author')
        tips = Tip.objects.annotate(rank=SearchRank(vector, query)).filter(
            rank__gt=0).order_by('-rank')
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
    else:
        sorted_tips = tips
    tags = Tag.objects.all().order_by('name')
    return render(request, template,
                  {'tips': sorted_tips, 'page_template': page_template,
                   'tags': tags})


def todays_tip(request):
    latest_tip = Tip.objects.latest()
    if latest_tip.timestamp.date() == now().date():
        tip = latest_tip
        return render(request, 'home/todays_tip.html', {'tip': tip})
    else:
        return render(request, 'home/todays_tip.html', {'tip': None})
