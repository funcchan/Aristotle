#!/usr/bin/env python
#
# @name: urls.py
# @create:
# @update:
# @author:
from django.conf.urls import patterns, include, url
from Aristotle.apps.qa import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.HomeView.as_view(), name='home-view'),
    url(r'^signin/', views.SignInView.as_view(), name='signin-view'),
    url(r'^signup/', views.SignUpView.as_view(), name='signup-view'),
)
