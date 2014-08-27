#!/usr/bin/env python
from django.conf.urls import patterns, include, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.home_page_view, name='home'),
    url(r'^index/$', views.home_page_view),
    url(r'^question/ask/$', views.ask_question_view, name='ask'),
    url(r'^question/(?P<question_id>\d+)/$', views.question_view, name='question'),
    url(r'^signup/$', views.signup_view, name='signup'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^user/(?P<user_id>\d+)/$', views.user_info_view, name='user')

)
