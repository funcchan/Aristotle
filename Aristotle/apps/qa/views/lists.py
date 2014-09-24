#!/usr/bin/env python
#
# @name: list.py
# @create: 24 September 2014 (Wednesday)
# @update: 24 September 2014 (Wednesday)
# @author: Z. Huang, Liangju
import logging
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Aristotle.apps.qa.search import search_question, search_user

from Aristotle.apps.qa.models import Question
from Aristotle.apps.qa.models import Tag
import Aristotle.apps.qa.settings as qa_settings

logger = logging.getLogger(__name__)


class HomeView(View):

    def get(self, request, *args, **kwargs):
        """Home page
        """
        limit = qa_settings.HOME_PAGE_SIZE
        questions = Question.objects.order_by('-created_time')[:limit]
        return render(request, 'qa/index.html', {'questions': questions})


class QuestionsView(View):

    def get(self, request, *args, **kwargs):
        """A list of questions
        """
        page = request.GET.get('page')
        sort = request.GET.get('sort')
        per_page = request.GET.get('pagesize')
        if not per_page:
            per_page = qa_settings.QUESTION_PAGE_SIZE
        if not sort:
            sort = 'newest'
        question_list = Question.objects
        if sort == 'votes':
            question_list = sorted(question_list.all(), key=lambda i: (
                i.votes_count, i.created_time), reverse=True)
        elif sort == 'answers':
            question_list = sorted(question_list.all(), key=lambda i: (
                i.solved, i.answers_count, i.created_time), reverse=True)
        elif sort == 'unanswered':
            question_list = sorted(question_list.filter(solved=False),
                                   key=lambda i: (i.answers_count,
                                                  i.votes_count,
                                                  i.created_time))
        elif sort == 'views':
            question_list = sorted(question_list.all(), key=lambda i: (
                i.hits_count, i.created_time), reverse=True)
        else:
            question_list = sorted(
                question_list.all(),
                key=lambda i: i.created_time, reverse=True)

        paginator = Paginator(question_list, per_page)
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
            questions = paginator.page(1)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)

        return render(request, 'qa/questions.html', {"questions": questions})


class TaggedQuestionsView(View):

    def get(self, request, *args, **kwargs):
        """A list of tagged questions
        """
        tag = kwargs['tag_name']
        page = request.GET.get('page')
        sort = request.GET.get('sort')
        per_page = request.GET.get('pagesize')
        if not per_page:
            per_page = qa_settings.QUESTION_PAGE_SIZE
        if not sort:
            sort = 'newest'
        tags = Tag.objects.filter(name=tag)
        question_list = []
        unsolved_question_list = []
        for t in tags:
            if not t.question.solved:
                unsolved_question_list.append(t.question)
            question_list.append(t.question)

        if sort == 'votes':
            question_list = sorted(question_list, key=lambda i: (
                i.votes_count, i.created_time), reverse=True)
        elif sort == 'answers':
            question_list = sorted(question_list, key=lambda i: (
                i.solved, i.answers_count, i.created_time), reverse=True)
        elif sort == 'unanswered':
            question_list = sorted(unsolved_question_list, key=lambda i: (
                i.answers_count, i.votes_count, i.created_time))
        elif sort == 'views':
            question_list = sorted(question_list, key=lambda i: (
                i.hits_count, i.created_time), reverse=True)
        else:
            question_list = sorted(
                question_list, key=lambda i: i.created_time, reverse=True)

        paginator = Paginator(question_list, per_page)
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
            questions = paginator.page(1)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)

        return render(request, 'qa/questions.html', {"questions": questions})


class TagsView(View):

    def get(self, request, *args, **kwargs):
        """A list of tags
        """
        page = request.GET.get('page')
        per_page = request.GET.get('pagesize') or qa_settings.TAG_PAGE_SIZE
        tag_list = Tag.objects.values('name').distinct()
        paginator = Paginator(tag_list, per_page)
        try:
            tags = paginator.page(page)
        except PageNotAnInteger:
            tags = paginator.page(1)
        except EmptyPage:
            tags = paginator.page(paginator.num_pages)
        return render(request, 'qa/tags.html', {'tags': tags})


class UsersView(View):

    def get(self, request):
        # TODO: Should render the 32*32 avatar for each users
        query = request.GET.get('query')
        if query:
            users = search_user(query)
        else:
            users = User.objects.order_by('username')
        return render(request, 'qa/users.html', {'users': users})

    def post(self, request):
        return redirect('/users/?query={0}'.format(request.POST.get('query')))


class SearchView(View):

    def get(self, request, *args, **kwargs):
        """Search page
        """
        return render(request, 'qa/search_question.html')

    def post(self, request, *args, **kwargs):
        try:
            search_query = request.POST.get('query')
            # TODO: Split by space

            if not search_query:
                raise Http404

            result = search_question(search_query)
            return render(request, 'qa/search_question.html',
                          {'result': result})
        except Exception as e:
            logger.error(str(e))
            return redirect('/search/')
