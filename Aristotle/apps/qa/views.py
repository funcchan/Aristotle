#!/usr/bin/env python
#
# @name: views.py
# @create: Aug. 25th, 2014
# @update: Sep. 4th, 2014
# @author: hitigon@gmail.com
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from .models import Question, Answer
from .models import QuestionComment, QuestionAppend
from .models import QuestionVote
from .models import AnswerComment, AnswerVote
from .models import AnswerAppend
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
            question = Question.objects.filter(id=int(qid))
            qcomment_qs = QuestionComment.objects.order_by(
                'created_time')
            qappend_qs = QuestionAppend.objects.order_by(
                'created_time')
            qvoteup_qs = QuestionVote.objects.order_by(
                'created_time').filter(vote_type=True)
            qvotedown_qs = QuestionVote.objects.order_by(
                'created_time').filter(vote_type=False)
            question = question.prefetch_related(
                Prefetch('questioncomment_set',
                         queryset=qcomment_qs, to_attr='comments'),
                Prefetch('questionappend_set',
                         queryset=qappend_qs, to_attr='appends'),
                Prefetch('questionvote_set',
                         queryset=qvoteup_qs, to_attr='upvotes'),
                Prefetch('questionvote_set',
                         queryset=qvotedown_qs, to_attr='downvotes'))

            # TODO Limiting the number of comments
            acomment_qs = AnswerComment.objects.order_by(
                'created_time')
            aappend_qs = AnswerAppend.objects.order_by('created_time')
            avoteup_qs = AnswerVote.objects.order_by(
                'created_time').filter(vote_type=True)
            avotedown_qs = AnswerVote.objects.order_by(
                'created_time').filter(vote_type=False)
            answers = Answer.objects.order_by('created_time').filter(
                question=question[0])
            answers = answers.prefetch_related(
                Prefetch('answercomment_set',
                         queryset=acomment_qs, to_attr='comments'),
                Prefetch('answervote_set',
                         queryset=avoteup_qs, to_attr='upvotes'),
                Prefetch('answervote_set',
                         queryset=avotedown_qs, to_attr='downvotes'),
                Prefetch('answerappend_set',
                         queryset=aappend_qs, to_attr='appends'))
            data = {
                'question': question[0],
                'answers': answers,
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
        err_redirect_uri = request.META['HTTP_REFERER']
        try:
            qid = kwargs['question_id']
            action = kwargs['action']
            redirect_uri = '/question/{0}/'.format(qid)

            question = Question.objects.filter(id=int(qid))

            if action == 'answer':
                self._answer(request, qid, question)
            elif action == 'edit':
                self._edit(request, qid, question)
            elif action == 'comment':
                self._comment(request, qid, question)
            elif action == 'append':
                self._append(request, qid, question)
            elif action == 'delete':
                redirect_uri = '/'
                self._delete(request, qid, question)
            elif action == 'upvote':
                self._vote(request, qid, question)
            elif action == 'downvote':
                self._vote(request, qid, question, False)
            return redirect(redirect_uri)
        except InvalidFieldError as e:
            msgs = e.messages
            for msg in msgs:
                messages.error(request, msg)
            return redirect(err_redirect_uri)
        except Exception as e:
            print(e)
            message = 'Error'
            messages.error(request, message)
            return redirect(err_redirect_uri)

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

    def _delete(self, request, qid, question):
        if request.user != question[0].author:
            raise Exception('Unauthorized action')
        question.delete()

    def _vote(self, request, qid, question, up=True):
        user = request.user
        voted = QuestionVote.objects.filter(question=question[0], user=user)
        if voted:
            if voted[0].vote_type != up:
                voted.delete()
        else:
            vote = QuestionVote.objects.create(
                question=question[0], user=user, vote_type=up)
            vote.save()

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
            print(e)
            message = 'Error'
            messages.error(request, message)
            return redirect('/question/ask/')


class AnswerActionView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        try:
            user = request.user
            aid = kwargs['answer_id']
            action = kwargs['action']
            answer = Answer.objects.get(id=int(aid))

            if action != 'edit':
                raise Exception('Unsupported action')
            if answer.author != user:
                raise Exception('Unauthorized action')
            return render(request, 'qa/edit_answer.html',
                          {'answer': answer})
        except Exception:
            # error handling is not done
            raise Http404

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """
        /answer/<:id>/accept/
        /answer/<:id>/edit/
        /answer/<:id>/comment/
        /answer/<:id>/append/
        /answer/<:id>/delete/
        /answer/<:id>/upvote/
        /answer/<:id>/downvote/
        """
        err_redirect_uri = request.META['HTTP_REFERER']
        try:
            aid = kwargs['answer_id']
            action = kwargs['action']
            answer = Answer.objects.filter(id=int(aid))
            redirect_uri = '/question/{0}/'.format(answer[0].question.id)
            if action == 'edit':
                self._edit(request, answer)
            elif action == 'append':
                self._append(request, answer)
            elif action == 'comment':
                self._comment(request, answer)
            elif action == 'delete':
                self._delete(request, answer)
            elif action == 'accept':
                self._accept(request, answer)
            elif action == 'upvote':
                self._vote(request, answer)
            elif action == 'downvote':
                self._vote(request, answer, False)
            return redirect(redirect_uri)
        except InvalidFieldError as e:
            msgs = e.messages
            for msg in msgs:
                messages.error(request, msg)
            return redirect(err_redirect_uri)
        except Exception as e:
            print(e)
            message = 'Error'
            messages.error(request, message)
            return redirect(err_redirect_uri)

    def _edit(self, request, answer):
        content = request.POST['content']
        err_msgs = []
        if not content:
            err_msgs.append('No content')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        if request.user != answer[0].author:
            raise Exception('Unauthorized action')
        answer.update(content=content)

    def _accept(self, request, answer):
        question = answer[0].question
        if request.user != question.author:
            raise Exception('Unauthorized action')
        # user cannot revoke or change this action
        # it is not a flexiable design
        # question.solved might need a one-to-one relationship
        # between question and answer
        # but, this current design makes the calculation of credits
        # much easier, since in this case we do not have to track
        # the credit changes for each answer and user
        if question.solved or answer[0].accepted:
            raise Exception('Unsupported action')
        answer.update(accepted=True)
        question.solved = True
        question.save()

    def _comment(self, request, answer):
        content = request.POST['answer_comment']
        err_msgs = []
        if not content:
            err_msgs.append('No content')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        comment = AnswerComment.objects.create(answer=answer[0],
                                               user=request.user,
                                               content=content)
        comment.save()

    def _append(self, request, answer):
        content = request.POST['answer_append']
        err_msgs = []
        if not content:
            err_msgs.append('No content')
        if request.user != answer[0].author:
            raise Exception('Unauthorized action')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        append = AnswerAppend.objects.create(answer=answer[0],
                                             content=content)
        append.save()

    def _delete(self, request, answer):
        if request.user != answer[0].author:
            raise Exception('Unauthorized action')
        question = answer[0].question
        if question.solved and answer[0].accepted:
            question.solved = False
            question.save()
        answer.delete()

    def _vote(self, request, answer, up=True):
        user = request.user
        voted = AnswerVote.objects.filter(answer=answer[0], user=user)
        if voted:
            if voted[0].vote_type != up:
                voted.delete()
        else:
            vote = AnswerVote.objects.create(
                answer=answer[0], user=user, vote_type=up)
            vote.save()
