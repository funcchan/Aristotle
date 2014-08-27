#!/usr/bin/env python
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', 'Aristotle.apps.qa.views.home'),
                       url(r'^signin/', 'Aristotle.apps.qa.views.signin'),
                       url(r'^signup/', 'Aristotle.apps.qa.views.signup'),
                       )
