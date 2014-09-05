#!/usr/bin/env python
#
# @name: urls.py
# @create:
# @update: Sep. 4nd, 2014
# @author:
from django.conf.urls import patterns, include, url
from Aristotle.apps.qa import views
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^signin/$', views.SignInView.as_view(), name='signin'),
    url(r'^signup/$', views.SignUpView.as_view(), name='signup'),
    url(r'^signout/$', views.SignOutView.as_view(), name='signout'),
    url(r'^user/(?P<user_id>[0-9]+)', views.UserProfileView.as_view(),
        name='user-setting-view'),
    url(r'^question/(?P<question_id>[0-9]+)/$', views.QuestionView.as_view(),
        name='question-view'),
    url(r'^question/ask/$',
        views.AskQuestionView.as_view(), name='ask-question'),
    url(r'^question/(?P<question_id>[0-9]+)/(?P<action>answer|edit|append|delete|comment|upvote|downvote)/$',
        views.QuestionActionView.as_view(),
        name='question-action'),
    url(r'^answer/(?P<answer_id>[0-9]+)/(?P<action>accept|edit|comment|delete|append|upvote|downvote)/$',
        views.AnswerActionView.as_view(), name='answer-action'),
    url(r'^questions/$', views.QuestionsView.as_view(), name='questions'),
    url(r'^questions/tagged/(?P<tag_name>[a-z0-9\-]+)/$', views.TaggedQuestionsView.as_view(), name='tagged-questions'),
    url(r'^tags/$', views.TagsView.as_view(), name='tags'),
)
