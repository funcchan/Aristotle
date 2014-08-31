#!/usr/bin/env python
#
# @name: views.py
# @create: Aug. 25th, 2014
# @update: Aug. 28th, 2014
# @author: hitigon@gmail.com
from django.shortcuts import render, redirect
from .models import Question
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from .errors import InvalidFieldError


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'qa/index.html')


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
            messages.error(request, e.message)
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
        return render(request, 'qa/question.html',
                      {'question_id': self.kwargs['question_id']})

    def post(self, request, *args, **kwargs):
        # TODO: Edit, Delete
        """
        1. Get POST info.
        2. Verify
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
        pass


class AskQuestion(View):
    def get(self, request, *args, **kwargs):
        """
        1. Normal page.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return render(request, 'qa/ask.html')

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
            question = Question.objects.create(title=title, content=content)
            question.save()
            return redirect('/question/{0}/'.format(question.id))
        except InvalidFieldError as e:
            msgs = e.messages
            for msg in msgs:
                messages.error(request, msg)
            return redirect('/ask')
        except Exception as e:
            messages.error(request, e.message)
            return redirect('/ask')



class AnswerView(View):
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
        pass