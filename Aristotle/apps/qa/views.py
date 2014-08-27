#!/usr/bin/env python
from . import models
from django.shortcuts import render

def home_page_view(request):
    # TODO: View for index
    """
    1. Check the user session
        - If login, get the user information

    2. Retrieval contents:
        - Newest Questions
            = Number of Votes
            = Number of Views
            = Tags
            = User
        - Hot Tags
        - Newest users

    3. Render the page

    :param request:
    :return:
    """
    return render(request, 'home.html')


def question_view(request, question_id):
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
    return render(request, 'question_content.html',
                  {'question_id': question_id})


def ask_question_view(request):
    # TODO: View for ask question
    return render(request, 'ask_question.html')


def signup_view(request):
    # TODO: View for sign up
    # TODO: Use OAUTH
    """
    1. Verify the session.
        - If already login, redirect to the home page.

    2.
        - If GET method, render the pages.
        - If POST method, handle the form information
            = Verify user information.
                ? Unique and Valid user name
                ? Unique and Valid Email address
                ? Valid and Confirmed Pwd
                ? Other information
            = If valid, redirect to successful page
            = Else, flash the alarm information.

    :param request:
    :return:
    """
    if request.method == 'POST':
        pass

    return render(request, 'signup.html')


def login_view(request):
    # TODO: View for sign in
    # TODO: Use OAUTH
    """
    1. Verify the session.
        - If already login, redirect to the home page.

    2.
        - If GET method, render the pages.
        - If POST method, handle the form information.
            = Verify user information. User name and pwd.
            = If correct, redirect the home page (or successful page).
            = Else, flash the alarm information.

    :param request:
    :return:
    """
    if request.method == 'POST':
        pass

    return render(request, 'login.html')


def user_info_view(request, user_id):
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
    return render(request, 'user_info.html', {'user_id': user_id})

