from django.shortcuts import render

# Create your views here.
from home.models import Tip, Tag


def index(request, template='home/tip_list.html',
          page_template='home/tip_list_page.html'):
    if request.is_ajax():
        template = page_template
    tips = Tip.objects.all()
    tags = Tag.objects.all().order_by('name')
    return render(request, template,
                  {'tips': tips, 'page_template': page_template, 'tags': tags})


def filter_tag(request, tag, template='home/tip_list.html',
               page_template='home/tip_list_page.html'):
    if request.is_ajax():
        template = page_template
    # vector = SearchVector('text')
    # query = SearchQuery(tag)
    # tips = Tip.objects.annotate(rank=SearchRank(vector, query)).order_by(
    #     '-rank')

    tips = Tip.objects.filter(text__search=tag)
    tags = Tag.objects.all().order_by('name')
    return render(request, template,
                  {'tips': tips, 'page_template': page_template, 'tags': tags})


def sort_tips(request, criteria, template='home/tip_list.html',
              page_template='home/tip_list_page.html'):
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
