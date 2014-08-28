#!/usr/bin/env python
#
# @name: views.py
# @create: Aug. 25th, 2014
# @update: Aug. 28th, 2014
# @author: hitigon@gmail.com
# from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from errors import InvalidFieldError


class HomeView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'qa/index.html')


class SignInView(View):

    def get(self, request, *args, **kwargs):
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
