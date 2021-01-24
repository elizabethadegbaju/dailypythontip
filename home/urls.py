"""dailypythontip home app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from home import views

app_name = 'home'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_tips, name='search-tips'),
    path('filter/<str:tag>/', views.filter_tag, name='filter-tag'),
    path('sort/<str:criteria>/', views.sort_tips, name='sort-tips'),
    path('today/', views.todays_tip, name='retrieve-today'),
    path('register/', views.create_account, name='register'),
    path('link_twitter/', views.link_twitter, name='link-twitter'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
]
