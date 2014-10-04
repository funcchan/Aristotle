#!/usr/bin/env python
#
# @name: list.py
# @create: 24 September 2014 (Wednesday)
# @update: 04 October 2014 (Saturday)
# @author: Z. Huang, Liangju
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Aristotle.apps.qa.models import Question
from Aristotle.apps.qa.models import Tag
from Aristotle.apps.qa.forms import SearchForm
from Aristotle.apps.qa.search import Search
from Aristotle.apps.qa.utils import form_errors_handler
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
        if not per_page or per_page == '0' or per_page == 0:
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
        if not per_page or per_page == '0' or per_page == 0:
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
        per_page = request.GET.get('pagesize')
        if not per_page or per_page == '0' or per_page == 0:
            per_page = qa_settings.TAG_PAGE_SIZE
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
        page = request.GET.get('page')
        per_page = request.GET.get('pagesize')
        if not per_page or per_page == '0' or per_page == 0:
            per_page = qa_settings.USER_PAGE_SIZE
        # TODO sort
        user_list = User.objects.all()
        paginator = Paginator(user_list, per_page)
        avatar_path = qa_settings.AVATAR_PATH + 'small/'
        try:
            users = paginator.page(page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)
        return render(request, 'qa/users.html',
                      {'users': users, 'avatar_path': avatar_path})


class SearchView(View):

    def get(self, request, *args, **kwargs):
        """Search page
        """
        query = request.GET.get('query')
        page = request.GET.get('page')
        per_page = request.GET.get('pagesize')
        if not per_page or per_page == '0' or per_page == 0:
            per_page = qa_settings.USER_PAGE_SIZE
        if query:
            search = Search(query)
            questions_list = search.questions()
        else:
            questions_list = []
        # sorting
        paginator = Paginator(questions_list, per_page)
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
            questions = paginator.page(1)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)
        form = SearchForm()
        return render(request, 'qa/search.html',
                      {'form': form, 'questions': questions})

    def post(self, request, *args, **kwargs):
        refer_url = '/search/'
        form = SearchForm(request.POST)
        if form.is_valid():
            query = request.POST.get('query')
            return redirect(refer_url + '?query={0}'.format(query))
        else:
            return form_errors_handler(request, form, refer_url)
