#!/usr/bin/env python
#
# @name: views.py
# @create: Aug. 25th, 2014
# @update: Aug. 27th, 2014
# @author: hitigon@gmail.com
# from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.generic import View


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
            return redirect('/signin')


class SignUpView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'qa/signup.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        # repassword = request.POST['repassword']
        user = User.objects.create_user(username, email, password)
        user.save()
        return redirect('/signin')
