#!/usr/bin/env python
#
# @name: views.py
# @create: Aug. 25th, 2014
# @update: Sep. 4rd, 2014
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
        """
        1. Find the question with question_id.
            - If not valid, redirect to 404

        2. Retrieval contents
            - Answers,
            - Users,
            - Comments,
            - Appends,
            - Tags.

        3. Render the page
        """
        # TODO answer order
        try:
            qid = kwargs['question_id']
            question = Question.objects.get(id=int(qid))
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


class QuestionActionView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        try:
            user = request.user
            qid = kwargs['question_id']
            action = kwargs['action']
            question = Question.objects.get(id=int(qid))

            if action != 'edit':
                raise Exception('Unsupported action')
            if question.author != user:
                raise Exception('Unauthorized action')
            return render(request, 'qa/edit_question.html',
                          {'question': question})
        except Exception:
            # error handling is not done
            raise Http404

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """
        /question/<:id>/answer/
        /question/<:id>/edit/
        /question/<:id>/comment/
        /question/<:id>/append/
        /question/<:id>/delete/
        /question/<:id>/upvote/
        /question/<:id>/downvote/
        """
        try:
            qid = kwargs['question_id']
            action = kwargs['action']
            error_url = '/question/{0}/'.format(qid)

            question = Question.objects.filter(id=int(qid))

            if action == 'answer':
                return self._answer(request, qid, question)
            elif action == 'edit':
                return self._edit(request, qid, question)
            elif action == 'comment':
                return self._comment(request, qid, question)
            elif action == 'append':
                return self._append(request, qid, question)
            elif action == 'delete':
                return self._delete(request, qid, question)
            elif action == 'upvote':
                return self._upvote(request, qid, question)
            elif action == 'downvote':
                return self._downvote(request, qid, question)

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

    def _edit(self, request, qid, question):
        title = request.POST['title']
        content = request.POST['content']
        err_msgs = []
        if not title:
            err_msgs.append('No title')
        if not content:
            err_msgs.append('No content')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        if request.user != question[0].author:
            raise Exception('Unauthorized action')
        question.update(title=title, content=content)
        return redirect('/question/{0}/'.format(qid))

    def _comment(self, request, qid, question):
        content = request.POST['question_comment']
        err_msgs = []
        if not content:
            err_msgs.append('No content')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        comment = QuestionComment.objects.create(question=question[0],
                                                 user=request.user,
                                                 content=content)
        comment.save()
        return redirect('/question/{0}/'.format(qid))

    def _append(self, request, qid, question):
        content = request.POST['question_append']
        err_msgs = []
        if not content:
            err_msgs.append('No content')
        if request.user != question[0].author:
            raise Exception('Unauthorized action')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        append = QuestionAppend.objects.create(question=question[0],
                                               content=content)
        append.save()
        return redirect('/question/{0}/'.format(qid))

    def _delete(self, request, qid, question):
        err_msgs = []
        if request.user != question[0].author:
            raise Exception('Unauthorized action')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        question.delete()  # TODO: Enable the cascading delete?
        return redirect('/')

    def _upvote(self, request, qid, question):
        # TODO: One user could ONLY vote one question for ONCE
        # if request.user == question[0].author:  # Don't vote yourself
        # raise Exception('Unauthorized action')
        up_votes = question[0].up_votes
        question.update(up_votes=up_votes + 1)
        return redirect('/question/{0}/'.format(qid))

    def _downvote(self, request, qid, question):
        # TODO: One user could ONLY vote one question for ONCE
        # if request.user == question[0].author:  # Don't vote yourself
        # raise Exception('Unauthorized action')
        down_votes = question[0].down_votes
        question.update(down_votes=down_votes + 1)
        return redirect('/question/{0}/'.format(qid))

    # TODO: Should _answer and _vote_answer be in another View?
    def _answer(self, request, qid, question):
        content = request.POST['answer_content']
        err_msgs = []
        if not content:
            err_msgs.append('No content')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        answer = Answer.objects.create(content=content,
                                       question=question[0],
                                       author=request.user)
        answer.save()
        return redirect('/question/{0}/'.format(qid))

    def _vote_answer(self, request, aid, answer):
        pass


class AskQuestionView(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """
        Render ask_question page.
        """
        return render(request, 'qa/ask_question.html')

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """
        Create a new question.
        """

        try:
            title = request.POST['title']
            content = request.POST['content']
            user = request.user
            err_msgs = []
            if not title:
                err_msgs.append('No title')
            if not content:
                err_msgs.append('No content')
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
            return redirect('/question/ask/')
        except Exception as e:
            message = 'Error'
            messages.error(request, message)
            return redirect('/question/ask/')
