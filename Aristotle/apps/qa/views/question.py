#!/usr/bin/env python
#
# @name:  question.py
# @create: 24 September 2014 (Wednesday)
# @update: 24 September 2014 (Wednesday)
# @author: Z. Huang, Liangju
import logging
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from Aristotle.apps.qa.models import Question, Answer
from Aristotle.apps.qa.models import QuestionComment, QuestionAppend
from Aristotle.apps.qa.models import QuestionVote, QuestionHit
from Aristotle.apps.qa.models import AnswerComment, AnswerVote
from Aristotle.apps.qa.models import AnswerAppend
from Aristotle.apps.qa.models import Tag
from Aristotle.apps.qa.forms import AskQuestionForm
from Aristotle.apps.qa.forms import EditQuestionForm, AnswerForm
from Aristotle.apps.qa.forms import CommentQuestionForm, AppendQuestionForm
from Aristotle.apps.qa.forms import EditAnswerForm, CommentAnswerForm
from Aristotle.apps.qa.forms import AppendAnswerForm
from Aristotle.apps.qa.utils import parse_listed_strs
from Aristotle.apps.qa.utils import form_errors_handler

logger = logging.getLogger(__name__)


class AskQuestionView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """Ask question page.
        """
        form = AskQuestionForm()
        return render(request, 'qa/ask_question.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """Add a new question
        if success redirect to the new question's page
        otherwise return error meesages
        """
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags = request.POST.get('tags')
        user = request.user
        refer_url = request.META.get('HTTP_REFERER') or '/'
        form = AskQuestionForm(request.POST)

        if form.is_valid():
            try:
                question = Question.objects.create(
                    title=title, content=content, author=user)
                question.save()
                if tags:
                    tags_list = parse_listed_strs(tags)
                    for name in tags_list:
                        tag = Tag.objects.create(name=name, question=question)
                        tag.save()
                return redirect('/question/{0}/'.format(question.id))
            except Exception as e:
                messages.error(request, e)
                return redirect(refer_url)
        else:
            return form_errors_handler(request, form, refer_url)


class QuestionView(View):

    def get(self, request, *args, **kwargs):
        """Question page
        """
        qid = kwargs['question_id']

        try:
            qid = int(qid)
        except TypeError:
            raise Http404()

        question_queryset = Question.objects.filter(id=qid)

        if not question_queryset:
            raise Http404()

        try:
            # store session for anonymous users
            question = question_queryset[0]
            if hasattr(request, 'session') and not request.session.session_key:
                request.session.save()
            session = request.session.session_key
            hitted = QuestionHit.objects.filter(
                question=question, session=session)
            if not hitted:
                ip = request.META['REMOTE_ADDR']
                hit = QuestionHit.objects.create(question=question,
                                                 ip=ip,
                                                 session=session)
                hit.save()
            # select comments, appends, votes, tags for the question

            # comments limits
            question_comments_queryset = QuestionComment.objects.order_by(
                'created_time')
            question_appends_queryset = QuestionAppend.objects.order_by(
                'created_time')
            question_voteups_queryset = QuestionVote.objects.order_by(
                '-created_time').filter(vote_type=True)
            question_votedowns_queryset = QuestionVote.objects.order_by(
                '-created_time').filter(vote_type=False)
            question_tags_queryset = Tag.objects.all()
            question_queryset = question_queryset.prefetch_related(
                Prefetch('questioncomment_set',
                         queryset=question_comments_queryset,
                         to_attr='comments'),
                Prefetch('questionappend_set',
                         queryset=question_appends_queryset,
                         to_attr='appends'),
                Prefetch('questionvote_set',
                         queryset=question_voteups_queryset,
                         to_attr='upvotes'),
                Prefetch('questionvote_set',
                         queryset=question_votedowns_queryset,
                         to_attr='downvotes'),
                Prefetch('tag_set',
                         queryset=question_tags_queryset,
                         to_attr='tags'))

            question = question_queryset[0]
            # TODO Limiting the number of comments
            answer_comments_queryset = AnswerComment.objects.order_by(
                'created_time')
            answer_appends_queryset = AnswerAppend.objects.order_by(
                'created_time')
            answer_upvotes_queryset = AnswerVote.objects.order_by(
                '-created_time').filter(vote_type=True)
            answer_downvotes_queryset = AnswerVote.objects.order_by(
                '-created_time').filter(vote_type=False)

            # answer limits
            answers = Answer.objects.filter(
                question=question)
            answers = answers.prefetch_related(
                Prefetch('answercomment_set',
                         queryset=answer_comments_queryset,
                         to_attr='comments'),
                Prefetch('answervote_set',
                         queryset=answer_upvotes_queryset,
                         to_attr='upvotes'),
                Prefetch('answervote_set',
                         queryset=answer_downvotes_queryset,
                         to_attr='downvotes'),
                Prefetch('answerappend_set',
                         queryset=answer_appends_queryset,
                         to_attr='appends'))
            answers = sorted(answers, key=lambda i: (
                i.accepted, i.abs_votes_count, i.created_time),
                reverse=True)
            question_comment_form = CommentQuestionForm()
            question_append_form = AppendQuestionForm()
            answer_form = AnswerForm()
            answer_comment_form = CommentAnswerForm()
            answer_append_form = AppendAnswerForm()
            data = {
                'question': question,
                'answers': answers,
                'answer_form': answer_form,
                'question_comment_form': question_comment_form,
                'question_append_form': question_append_form,
                'answer_comment_form': answer_comment_form,
                'answer_append_form': answer_append_form,
            }

            return render(request, 'qa/question.html', data)
        except Exception as e:
            logger.error(str(e))
            return HttpResponse(status=500)


class QuestionActionView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """render a question edition page
        """
        user = request.user
        qid = kwargs['question_id']
        action = kwargs['action']
        try:
            qid = int(qid)
        except TypeError:
            raise Http404()

        if action != 'edit':
            return redirect('/question/%d/' % qid)

        question_queryset = Question.objects.filter(id=qid)
        if not question_queryset:
            raise Http404()

        if question_queryset[0].author != user:
            return HttpResponse(status=403)

        # instead of using prefetch, we can
        # use get_tags method defined in the model
        # prefetch might be a better solution,
        # since it combines data from other tables
        # into a single model
        question_tags_queryset = Tag.objects.all()
        question_queryset = question_queryset.prefetch_related(
            Prefetch('tag_set', queryset=question_tags_queryset,
                     to_attr='tags'))
        question = question_queryset[0]
        tags_list = ', '.join([tag.name for tag in question.tags])
        initial = {
            'title': question.title,
            'content': question.content,
            'tags': tags_list,
        }
        form = EditQuestionForm(initial=initial)
        return render(request, 'qa/edit_question.html',
                      {'question': question, 'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """Multiple actions for questions
        /question/<:id>/answer/
        /question/<:id>/edit/
        /question/<:id>/comment/
        /question/<:id>/append/
        /question/<:id>/delete/
        /question/<:id>/upvote/
        /question/<:id>/downvote/
        """
        qid = kwargs['question_id']
        action = kwargs['action']
        refer_url = request.META.get('HTTP_REFERER') or '/'
        try:
            qid = int(qid)
        except TypeError:
            raise Http404()
        try:
            question_queryset = Question.objects.filter(id=qid)

            if action == 'answer':
                return self._answer(request, question_queryset, refer_url)
            elif action == 'edit':
                return self._edit(request, question_queryset, refer_url)
            elif action == 'comment':
                return self._comment(request, question_queryset, refer_url)
            elif action == 'append':
                return self._append(request, question_queryset, refer_url)
            elif action == 'delete':
                return self._delete(request, question_queryset)
            elif action == 'upvote':
                return self._vote(request, question_queryset)
            elif action == 'downvote':
                return self._vote(request, question_queryset, False)
        except Exception as e:
            messages.error(request, str(e))
            return redirect(refer_url)

    def _edit(self, request, question_queryset, refer_url):
        """Edit a question by its author
        """
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags = request.POST.get('tags')
        form = EditQuestionForm(request.POST)

        if form.is_valid():
            question = question_queryset[0]
            if request.user != question.author:
                return HttpResponse(status=403)
            question_queryset.update(
                title=title, content=content, updated_time=timezone.now())
            if tags:
                tags_list = parse_listed_strs(tags)
                stored_tags = set(
                    question.tag_set.values_list('name', flat=True))
                inter = tags_list & stored_tags
                to_del = stored_tags - inter
                to_add = tags_list - inter
                for name in to_del:
                    Tag.objects.filter(name=name, question=question).delete()
                for name in to_add:
                    Tag.objects.create(name=name, question=question).save()
            redirect_uri = '/question/{0}/'.format(question.id)
            return redirect(redirect_uri)
        else:
            return form_errors_handler(request, form, refer_url)

    def _comment(self, request, question_queryset, refer_url):
        """Comment a question by users
        """
        content = request.POST.get('question_comment_content')
        form = CommentQuestionForm(request.POST)
        if form.is_valid():
            question = question_queryset[0]
            comment = QuestionComment.objects.create(question=question,
                                                     user=request.user,
                                                     content=content)
            comment.save()
            redirect_uri = '/question/{0}/'.format(question.id)
            return redirect(redirect_uri)
        else:
            return form_errors_handler(request, form, refer_url)

    def _append(self, request, question_queryset, refer_url):
        """Append a item for the question by its author
        """
        content = request.POST['question_append_content']
        form = AppendQuestionForm(request.POST)
        if form.is_valid():
            question = question_queryset[0]
            if request.user != question.author:
                return HttpResponse(status=403)
            append = QuestionAppend.objects.create(question=question,
                                                   content=content)
            append.save()
            redirect_uri = '/question/{0}/'.format(question.id)
            return redirect(redirect_uri)
        else:
            return form_errors_handler(request, form, refer_url)

    def _delete(self, request, question_queryset):
        """Delete a question by its author
        """
        if request.user != question_queryset[0].author:
            return HttpResponse(status=403)
        question_queryset.delete()
        return redirect('/')

    def _vote(self, request, question_queryset, up=True):
        """vote down or vote up for a question
        the author cannot vote
        """
        user = request.user
        question = question_queryset[0]
        voted = QuestionVote.objects.filter(question=question, user=user)
        if user != question.author:
            if voted:
                if voted[0].vote_type != up:
                    voted.delete()
            else:
                vote = QuestionVote.objects.create(
                    question=question, user=user, vote_type=up)
                vote.save()
        redirect_uri = '/question/{0}/'.format(question.id)
        return redirect(redirect_uri)

    def _answer(self, request, question_queryset, refer_url):
        """Answer a question by users
        """
        content = request.POST.get('answer_content')
        form = AnswerForm(request.POST)
        if form.is_valid():
            question = question_queryset[0]
            answer = Answer.objects.create(content=content,
                                           question=question,
                                           author=request.user)
            answer.save()
            redirect_uri = '/question/{0}/'.format(question.id)
            return redirect(redirect_uri)
        else:
            return form_errors_handler(request, form, refer_url)


class AnswerActionView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        user = request.user
        aid = kwargs['answer_id']
        action = kwargs['action']
        try:
            aid = int(aid)
        except TypeError:
            raise Http404()
        try:
            answer = Answer.objects.get(id=aid)
            if action != 'edit':
                return redirect('/question/{0}'.format(answer.question.id))
            if answer.author != user:
                return HttpResponse(status=403)
            initial = {
                'answer_content': answer.content,
            }
            form = EditAnswerForm(initial=initial)
            return render(request, 'qa/edit_answer.html',
                          {'answer': answer, 'form': form})
        except Exception as e:
            logger.error(str(e))
            raise Http404()

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
        refer_url = request.META.get('HTTP_REFERER') or '/'
        aid = kwargs['answer_id']
        action = kwargs['action']
        try:
            aid = int(aid)
        except TypeError:
            raise Http404()
        try:
            answer_queryset = Answer.objects.filter(id=aid)
            if action == 'edit':
                return self._edit(request, answer_queryset, refer_url)
            elif action == 'append':
                return self._append(request, answer_queryset, refer_url)
            elif action == 'comment':
                return self._comment(request, answer_queryset, refer_url)
            elif action == 'delete':
                return self._delete(request, answer_queryset)
            elif action == 'accept':
                return self._accept(request, answer_queryset)
            elif action == 'upvote':
                return self._vote(request, answer_queryset)
            elif action == 'downvote':
                return self._vote(request, answer_queryset, False)
        except Exception as e:
            messages.error(request, str(e))
            return redirect(refer_url)

    def _edit(self, request, answer_queryset, refer_url):
        """Edit answer by its author
        """
        content = request.POST.get('answer_content')
        answer = answer_queryset[0]
        if request.user != answer.author:
            return HttpResponse(status=403)
        form = EditAnswerForm(request.POST)
        if form.is_valid():
            answer_queryset.update(
                content=content, updated_time=timezone.now())
            redirect_uri = '/question/{0}/'.format(answer.question.id)
            return redirect(redirect_uri)
        else:
            return form_errors_handler(request, form, refer_url)

    def _accept(self, request, answer_queryset):
        """Accept an answer by the question's author
        """
        answer = answer_queryset[0]
        question = answer.question
        redirect_uri = '/question/{0}/'.format(answer.question.id)
        if request.user != question.author:
            return HttpResponse(status=403)
        # user cannot revoke or change this action
        # it is not a flexiable design
        # question.solved might need a one-to-one relationship
        # between question and answer
        # but, this current design makes the calculation of credits
        # much easier, since in this case we do not have to track
        # the credit changes for each answer and user
        if not question.solved and not answer.accepted:
            answer_queryset.update(accepted=True, accepted_time=timezone.now())
            question.solved = True
            question.save()
        return redirect(redirect_uri)

    def _comment(self, request, answer_queryset, refer_url):
        """Comment an answer
        """
        answer = answer_queryset[0]
        content = request.POST.get('answer_comment_content')
        form = CommentAnswerForm(request.POST)
        if form.is_valid():
            comment = AnswerComment.objects.create(answer=answer,
                                                   user=request.user,
                                                   content=content)
            comment.save()
            redirect_uri = '/question/{0}/'.format(answer.question.id)
            return redirect(redirect_uri)
        else:
            return form_errors_handler(request, form, refer_url)

    def _append(self, request, answer_queryset, refer_url):
        """Append contents to an answer by the answer's author
        """
        content = request.POST.get('answer_append_content')
        answer = answer_queryset[0]
        if request.user != answer.author:
            return HttpResponse(status=403)

        form = AppendAnswerForm(request.POST)
        if form.is_valid():
            append = AnswerAppend.objects.create(answer=answer,
                                                 content=content)
            append.save()
            redirect_uri = '/question/{0}/'.format(answer.question.id)
            return redirect(redirect_uri)
        else:
            return form_errors_handler(request, form, refer_url)

    def _delete(self, request, answer_queryset):
        """Delete an answer by its author
        """
        answer = answer_queryset[0]
        if request.user != answer.author:
            return HttpResponse(status=403)
        question = answer.question
        if question.solved and answer.accepted:
            question.solved = False
            question.save()
        answer_queryset.delete()
        redirect_uri = '/question/{0}/'.format(answer.question.id)
        return redirect(redirect_uri)

    def _vote(self, request, answer_queryset, up=True):
        """Vote for the answer
        The author cannot vote
        """
        answer = answer_queryset[0]
        user = request.user
        voted = AnswerVote.objects.filter(answer=answer, user=user)
        if user != answer.author:
            if voted:
                if voted[0].vote_type != up:
                    voted.delete()
            else:
                vote = AnswerVote.objects.create(
                    answer=answer, user=user, vote_type=up)
                vote.save()
        redirect_uri = '/question/{0}/'.format(answer.question.id)
        return redirect(redirect_uri)
