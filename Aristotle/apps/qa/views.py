#!/usr/bin/env python
#
# @name: views.py
# @create: Aug. 25th, 2014
# @update: Sep. 3rd, 2014
# @author: hitigon@gmail.com
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.decorators import login_required

from .models import Question, Answer
from .models import QuestionComment, QuestionAppend
from .errors import InvalidFieldError


class HomeView(View):

    def get(self, request, *args, **kwargs):
        """
        """
        # TODO list order, limits
        questions = Question.objects.order_by('created_time')[:10]
        return render(request, 'qa/index.html', {'questions': questions})


class SignInView(View):

    def get(self, request, *args, **kwargs):
        # TODO: Check the session
        """
        Verify the session.
            - If already login, redirect to the home page.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return render(request, 'qa/signin.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')
        else:
            msg = 'Username or password is not correct'
            messages.error(request, msg)
            return redirect('/signin')


class SignUpView(View):

    def get(self, request, *args, **kwargs):
        # TODO: Check the session
        """
        Verify the session.
            - If already login, redirect to the home page.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return render(request, 'qa/signup.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repassword = request.POST['repassword']
        err_msgs = []
        if not username:
            err_msgs.append('Username is required')
        if not email:
            err_msgs.append('Email is required')
        if not password or not repassword:
            err_msgs.append('Passwords are required')
        if password != repassword:
            err_msgs.append('Two passwords are not identical')
        try:
            if err_msgs:
                raise InvalidFieldError(messages=err_msgs)
            user = User.objects.create_user(username, email, password)
            user.save()
            return redirect('/signin')

        except InvalidFieldError as e:
            msgs = e.messages
            for msg in msgs:
                messages.error(request, msg)
            return redirect('/signup')
        except Exception as e:
            message = 'Error'
            messages.error(request, message)
            return redirect('/signup')


class SignOutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/signin')


# Start by Liangju
# @ Aug. 28th, 2014
class UserProfileView(View):
    template_name = 'qa/user_profile.html'

    def get(self, request, *args, **kwargs):
        # TODO: View for user info
        """
        1. Retrieval the User data by User ID
            - If no such user. Redirect to non-existing page.

        2. Check the current user login status
            - If it is the page for current user, there should be more links, such as Edit, My Question, Modification, etc.
            - If it is the page for other users, just show the necessary information.

        3. Render the page

        :param request:
        :return:
        """
        return render(request, 'qa/user_profile.html',
                      {'user_id': self.kwargs['user_id']})


class QuestionView(View):

    def get(self, request, *args, **kwargs):
        # TODO: View for the question content
        """
        1. Search the question with question_id.
            - If not valid, redirect to 404

        2. Retrieval contents
            - Answers,
            - Users,
            - Comments,
            - Appends,
            - Tags.

        3. Render the page

        :param request:
        :param question_id:
        :return:
        """
        # TODO answer order
        try:
            qid = kwargs['question_id']
            user = request.user
            question = Question.objects.get(id=int(qid))
            if 'action' in kwargs and kwargs['action'] == 'edit':
                if user.is_authenticated() and question.author == user:
                    return render(request, 'qa/edit_question.html',
                                  {'question': question})
                else:
                    raise Exception('Unauthorized')
            question_comments = QuestionComment.objects.order_by(
                'created_time').filter(question=question)
            question_appends = QuestionAppend.objects.order_by(
                'created_time').filter(question=question)
            answers = Answer.objects.order_by('created_time').filter(
                question=question)
            data = {
                'question': question,
                'answers': answers,
                'question_appends': question_appends,
                'question_comments': question_comments,
            }
            return render(request, 'qa/question.html', data)
        except Exception as e:
            print(e)
            raise Http404

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        user = request.user
        qid = kwargs['question_id']
        action = kwargs['action']

        err_msgs = []
        error_url = '/'

        if action == 'edit':
            title = request.POST['title']
            content = request.POST['content']
            if not title:
                err_msgs.append('No title')
            if not content:
                err_msgs.append('No content')
            error_url = '/question/{0}/edit/'.format(qid)
        elif action == 'append':
            question_append = request.POST['question_append']
            if not question_append:
                err_msgs.append('No append content')
            error_url = '/question/{0}/'.format(qid)
        elif action == 'delete':
            error_url = '/question/{0}/'.format(qid)
        elif action == 'comment':
            question_comment = request.POST['question_comment']
            if not question_comment:
                err_msgs.append('No comment content')
            error_url = '/question/{0}/'.format(qid)
        try:
            if err_msgs:
                raise InvalidFieldError(messages=err_msgs)

            question = Question.objects.filter(id=int(qid))

            if action == 'edit':
                if user != question[0].author:
                    raise Exception('Unauthorized')
                question.update(title=title, content=content)
                return redirect('/question/{0}/'.format(qid))
            elif action == 'append':
                if user != question[0].author:
                    raise Exception('Unauthorized')
                append = QuestionAppend.objects.create(question=question[0],
                                                       content=question_append)
                append.save()
                return redirect('/question/{0}/'.format(qid))
            elif action == 'delete':
                if user != question[0].author:
                    raise Exception('Unauthorized')
                question.delete()
                return redirect('/')
            elif action == 'comment':
                comment = QuestionComment.objects.create(question=question[0],
                                                         user=user,
                                                         content=question_comment)
                comment.save()
                return redirect('/question/{0}/'.format(qid))
        except InvalidFieldError as e:
            msgs = e.messages
            for msg in msgs:
                messages.error(request, msg)
            return redirect(error_url)
        except Exception as e:
            print(e)
            message = 'Error'
            messages.error(request, message)
            return redirect(error_url)


class AskQuestion(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """
        1. Normal page.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return render(request, 'qa/ask.html')

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """
        1. Insert into DB
        2. Redirect to target question Page
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        title = request.POST['title']
        content = request.POST['content']
        user = request.user
        # TODO: Complete the user_id field
        # Might need require the Sessions and Cookie

        err_msgs = []
        if not title:
            err_msgs.append('No title')
        if not content:
            err_msgs.append('No content')

        try:
            if err_msgs:
                raise InvalidFieldError(messages=err_msgs)
            question = Question.objects.create(title=title, content=content,
                                               author=user)
            question.save()
            return redirect('/question/{0}/'.format(question.id))
        except InvalidFieldError as e:
            msgs = e.messages
            for msg in msgs:
                messages.error(request, msg)
            return redirect('/ask')
        except Exception as e:
            message = 'Error'
            messages.error(request, message)
            return redirect('/ask')


class AnswerView(View):

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # TODO:
        """
        1. Get POST info.
        2. Verify
            - Target question number
            - Length
            - Tag
            - etc.
        3. Insert to table
        4. Redirect to the current question page.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user = request.user
        qid = self.kwargs['question_id']
        content = request.POST['answer_content']
        err_msgs = []
        if not content:
            err_msgs.append('No content')

        try:
            if err_msgs:
                raise InvalidFieldError(messages=err_msgs)
            question = Question.objects.get(id=int(qid))
            answer = Answer.objects.create(content=content,
                                           question=question, author=user)
            answer.save()
            # print(answer)
            return redirect('/question/{0}/'.format(qid))
        except InvalidFieldError as e:
            msgs = e.messages
            for msg in msgs:
                messages.error(request, msg)
            return redirect('/ask')
        except Exception:
            message = 'Error'
            messages.error(request, message)
            return redirect('/question/{0}/'.format(qid))
