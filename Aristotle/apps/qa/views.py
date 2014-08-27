#!/usr/bin/env python
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


def home(request):
    return render(request, 'qa/index.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('/')
        else:
            return redirect('/signin')

    elif request.method == 'GET':
        return render(request, 'qa/signin.html')
    else:
        response = HttpResponse()
        response.status_code = 405
        return response


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        # repassword = request.POST['repassword']
        user = User.objects.create_user(username, email, password)
        user.save()
        return redirect('/signin')
    elif request.method == 'GET':
        return render(request, 'qa/signup.html')
