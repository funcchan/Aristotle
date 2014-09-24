#!/usr/bin/env python
#
# @name: urls.py
# @create:
# @update: Sep. 24th, 2014
# @author: Z. Huang, Liangju
from django.conf.urls import patterns, include, url
from Aristotle.apps.qa.views import user, lists, question
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^signin/$', user.SignInView.as_view(), name='signin'),
    url(r'^signup/$', user.SignUpView.as_view(), name='signup'),
    url(r'^signout/$', user.SignOutView.as_view(), name='signout'),
    url(r'^activate/$',
        user.ActivateView.as_view(), name='activate-index'),
    url(r'^activate/(?P<activation_code>[\w0-9]+)/$',
        user.ActivateView.as_view(), name='activate'),
    url(r'^reset/$',
        user.ResetPasswordView.as_view(), name='reset'),
    url(r'^reset/(?P<reset_code>[\w0-9]+)/$',
        user.ResetPasswordView.as_view(), name='reset-password'),
    url(r'^profile/$',
        user.ProfileView.as_view(), name='profile'),
    url(r'^profile/(?P<user_id>[0-9]+)/$',
        user.ProfileView.as_view(), name='profile'),
    url(r'^profile/edit/$',
        user.EditProfileView.as_view(), name='edit-profile'),
    url(r'^profile/(?P<user_id>[0-9]+)/edit/$',
        user.EditProfileView.as_view(), name='edit-profile'),
    url(r'^profile/avatar/$',
        user.EditAvatarView.as_view(), name='edit-avatar'),
    url(r'^profile/(?P<user_id>[0-9]+)/avatar/$',
        user.EditAvatarView.as_view(), name='edit-avatar'),
    url(r'^profile/account/$',
        user.EditAccountView.as_view(), name='edit-account'),
    url(r'^profile/(?P<user_id>[0-9]+)/account/$',
        user.EditAccountView.as_view(), name='edit-account'),
    url(r'^question/(?P<question_id>[0-9]+)/$',
        question.QuestionView.as_view(),
        name='question-view'),
    url(r'^question/ask/$',
        question.AskQuestionView.as_view(), name='ask-question'),
    url(r'^question/(?P<question_id>[0-9]+)/(?P<action>answer|edit|append|delete|comment|upvote|downvote)/$',
        question.QuestionActionView.as_view(),
        name='question-action'),
    url(r'^answer/(?P<answer_id>[0-9]+)/(?P<action>accept|edit|comment|delete|append|upvote|downvote)/$',
        question.AnswerActionView.as_view(), name='answer-action'),
    url(r'^$', lists.HomeView.as_view(), name='home'),
    url(r'^questions/$', lists.QuestionsView.as_view(), name='questions'),
    url(r'^questions/tagged/(?P<tag_name>[\w0-9\-]+)/$',
        lists.TaggedQuestionsView.as_view(), name='tagged-questions'),
    url(r'^tags/$', lists.TagsView.as_view(), name='tags'),
    url(r'^users/$', lists.UsersView.as_view(), name='user-list'),
    url(r'^users/?query=[\w0-9]+/$', lists.UsersView.as_view(),
        name='user-list'),
    url(r'^search/$', lists.SearchView.as_view(), name='search'),
)
