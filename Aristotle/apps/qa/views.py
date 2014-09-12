#!/usr/bin/env python
#
# @name: views.py
# @create: Aug. 25th, 2014
# @update: Sep. 11th, 2014
# @author: Z. Huang, Liangju
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Aristotle.apps.qa.search import search_question, search_user

from models import Question, Answer
from models import QuestionComment, QuestionAppend
from models import QuestionVote, QuestionHit
from models import AnswerComment, AnswerVote
from models import AnswerAppend
from models import Member, Activation
from models import Tag, ResetPassword
from forms import SignInForm, SignUpForm
from notification import EmailNotification
from errors import InvalidFieldError
from utils import parse_listed_strs


class HomeView(View):

    def get(self, request, *args, **kwargs):
        """test
        """
        # TODO list order, limits
        questions = Question.objects.order_by('-created_time')
        return render(request, 'qa/index.html', {'questions': questions})


class SignInView(View):

    def get(self, request, *args, **kwargs):
        """render login page
        if user has logged in, redirect back to referer page or home page
        """
        if request.user.is_authenticated():
            ref = request.META.get('HTTP_REFERER')
            return redirect(ref or '/')
        form = SignInForm()
        next_url = request.GET.get('next')
        return render(request, 'qa/signin.html',
                      {'form': form, 'next': next_url or ''})

    def post(self, request, *args, **kwargs):
        """login action
        using django form to verify the form (username and password)
        using django auth and user model to login
        if the form is valid:
            if login is valid:
                redirect to previous visiting page or home page
            otherwise:
                redirect to login page and show error messages
        otherwise:
            redirect to login page show error messages
        """
        form = SignInForm(request.POST)
        next_url = request.POST.get('next')
        refer_url = request.META.get('HTTP_REFERER')
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                ip = request.META['REMOTE_ADDR']
                login(request, user)
                Member.objects.filter(user=user).update(last_login_ip=ip)
                return redirect(next_url or '/')
            else:
                msg = 'username or password is not correct'
                messages.error(request, msg)
                return redirect(refer_url)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    msg = '%s: %s' % (field, error)
                    messages.error(request, msg)
            return redirect(refer_url)


class SignUpView(View):

    def get(self, request, *args, **kwargs):
        """render sign up page
        if user has logged in, redirect back to referer page or home page
        """
        if request.user.is_authenticated():
            ref = request.META.get('HTTP_REFERER')
            return redirect(ref or '/')
        form = SignUpForm()
        return render(request, 'qa/signup.html', {'form': form})

    def post(self, request, *args, **kwargs):
        """sign up action
        verify the form by django model
        if the form is valid, then add a new user,
        an activation code and send an email notification
        to user's email
        Any error happens, redirect to the refer url with
        flash messages
        """
        form = SignUpForm(request.POST)
        refer_url = request.META.get('HTTP_REFERER')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    username=username, email=email,
                    password=password)
                user.save()
                Member.objects.create(user=user).save()
                Activation.objects.create(user=user).save()
                # only for testing
                # TODO handle emails concurrently (async queue)
                EmailNotification(user).send_verfication()
                return redirect('/signin/')
            except Exception as e:
                messages.error(request, str(e))
                return redirect(refer_url)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    msg = '%s: %s' % (field, error)
                    messages.error(request, msg)
            return redirect(refer_url)


class ActivateView(View):

    def get(self, request, *args, **kwargs):
        """ Active user's account with a random code
        """
        try:

            code = kwargs['activation_code']

            result = Activation.objects.get(code=code)
            if result:
                if not result.is_active and result.expire_time > timezone.now():
                    result.is_active = True
                    result.save()
                    return render(request, 'qa/activation.html')
                else:
                    raise Exception('Expired code')
            else:
                raise Exception('No such code')
        except Exception:
            raise Http404()


class ResetPasswordView(View):

    def get(self, request, *args, **kwargs):
        if kwargs and 'reset_code' in kwargs:
            code = kwargs['reset_code']
            return render(request, 'qa/reset_password.html', {'code': code})
        else:
            return render(request, 'qa/reset.html')

    def post(self, request, *args, **kwargs):
        try:
            if kwargs and 'reset_code' in kwargs:
                password = request.POST.get('password')
                repassword = request.POST.get('repassword')
                code = kwargs['reset_code']
                # TODO verfiy password
                if password != repassword:
                    raise Http404()
                result = ResetPassword.objects.get(code=code)
                if result:
                    if result.expire_time > timezone.now():
                        result.user.set_password(password)
                        result.user.save()
                        return redirect('/signin/')
                    else:
                        raise Exception('Expired code')
                else:
                    raise Exception('No such code')
            else:
                email = request.POST.get('email')
                user = User.objects.get(email=email)
                # try to catch errors
                EmailNotification(user).send_reset_password()
                return redirect('/reset/')
        except Exception as e:
            print(e)
            raise Http404()


class SignOutView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/signin')


class ProfileView(View):

    def get(self, request, *args, **kwargs):
        try:
            if 'user_id' in kwargs:
                uid = kwargs['user_id']
                user = User.objects.get(id=int(uid))
            else:
                user = request.user
                if user.is_anonymous():
                    raise Exception('Unauthorized action')
            questions = Question.objects.order_by(
                '-created_time').filter(author=user)
            answers = Answer.objects.order_by(
                '-created_time').filter(author=user)
            return render(request, 'qa/profile.html',
                          {'user': user,
                           'questions': questions,
                           'answers': answers})
        except Exception:
            raise Http404


class EditProfileView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            if 'user_id' in kwargs:
                uid = kwargs['user_id']
                user = User.objects.get(id=int(uid))
                if user != request.user:
                    raise Http404
            else:
                user = request.user
            return render(request, 'qa/edit_profile.html', {'user': user})
        except Exception:
            raise Http404

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        try:
            if 'user_id' in kwargs:
                uid = kwargs['user_id']
                user = User.objects.get(id=int(uid))

                if user != request.user:
                    raise Http404
            else:
                user = request.user

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            occupation = request.POST.get('occupation')
            education = request.POST.get('education')
            address = request.POST.get('address')
            phone = request.POST.get('phone')
            company = request.POST.get('company')
            website = request.POST.get('website')
            interests = request.POST.get('interests')
            bio = request.POST.get('bio')

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            user.member.age = int(age)
            user.member.gender = gender
            user.member.occupation = occupation
            user.member.education = education
            user.member.address = address
            user.member.phone = phone
            user.member.company = company
            user.member.website = website
            user.member.interests = interests
            user.member.bio = bio
            user.member.update()
            return redirect('/profile/edit/')
        except Exception as e:
            print(e)
            raise Http404


class EditAccountView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        try:
            if 'user_id' in kwargs:
                uid = kwargs['user_id']
                user = User.objects.get(id=int(uid))
                if user != request.user:
                    raise Http404
            else:
                user = request.user
            return render(request, 'qa/edit_account.html', {'user': user})
        except Exception:
            raise Http404

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        password = request.POST.get('password')
        username = request.POST.get('username')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        err_msgs = []
        if not username:
            err_msgs.append('Username is required')
        if not email:
            err_msgs.append('Email is required')
        if not password:
            err_msgs.append('Password is required')

        try:
            if err_msgs:
                raise InvalidFieldError(messages=err_msgs)
            if 'user_id' in kwargs:
                uid = kwargs['user_id']
                user = User.objects.get(id=int(uid))

                if user != request.user:
                    raise Http404
            else:
                user = request.user
            if new_password:
                if user.check_password(password):
                    user.set_password(new_password)
                else:
                    raise Exception('Unauthorized action')
            user.username = username
            user.email = email
            user.save()
            return redirect('/signout/')
        except InvalidFieldError as e:
            msgs = e.messages
            for msg in msgs:
                messages.error(request, msg)
            return redirect('/profile/account/')
        except Exception as e:
            messages.error(request, e.message)
            return redirect('/profile/account/')


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
            # store session for anonymous users
            if hasattr(request, 'session') and not request.session.session_key:
                request.session.save()
            session = request.session.session_key
            hitted = QuestionHit.objects.filter(
                question=question[0], session=session)
            if not hitted:
                ip = request.META['REMOTE_ADDR']
                hit = QuestionHit.objects.create(question=question[0],
                                                 ip=ip,
                                                 session=session)
                hit.save()
            qcomment_qs = QuestionComment.objects.order_by(
                'created_time')
            qappend_qs = QuestionAppend.objects.order_by(
                'created_time')
            qvoteup_qs = QuestionVote.objects.order_by(
                'created_time').filter(vote_type=True)
            qvotedown_qs = QuestionVote.objects.order_by(
                'created_time').filter(vote_type=False)
            qtags_qs = Tag.objects.all()
            question = question.prefetch_related(
                Prefetch('questioncomment_set',
                         queryset=qcomment_qs, to_attr='comments'),
                Prefetch('questionappend_set',
                         queryset=qappend_qs, to_attr='appends'),
                Prefetch('questionvote_set',
                         queryset=qvoteup_qs, to_attr='upvotes'),
                Prefetch('questionvote_set',
                         queryset=qvotedown_qs, to_attr='downvotes'),
                Prefetch('tag_set', queryset=qtags_qs, to_attr='tags'))

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


class QuestionsView(View):

    def get(self, request, *args, **kwargs):

        PER_PAGE = 5
        page = request.GET.get('page')
        sort = request.GET.get('sort')
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

        paginator = Paginator(question_list, PER_PAGE)
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
            questions = paginator.page(1)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)

        return render(request, 'qa/questions.html', {"questions": questions})


class TaggedQuestionsView(View):

    def get(self, request, *args, **kwargs):

        PER_PAGE = 5
        tag = kwargs['tag_name']
        page = request.GET.get('page')
        sort = request.GET.get('sort')
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

        paginator = Paginator(question_list, PER_PAGE)
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
            questions = paginator.page(1)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)

        return render(request, 'qa/questions.html', {"questions": questions})


class TagsView(View):

    def get(self, request, *args, **kwargs):
        PER_PAGE = 10
        page = request.GET.get('page')
        tag_list = Tag.objects.values('name').distinct()
        paginator = Paginator(tag_list, PER_PAGE)
        try:
            tags = paginator.page(page)
        except PageNotAnInteger:
            tags = paginator.page(1)
        except EmptyPage:
            tags = paginator.page(paginator.num_pages)
        return render(request, 'qa/tags.html', {'tags': tags})


class UsersView(View):

    def get(self, request, *args, **kwargs):
        pass


class QuestionActionView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        try:
            user = request.user
            qid = kwargs['question_id']
            action = kwargs['action']
            question = Question.objects.filter(id=int(qid))
            qtags_qs = Tag.objects.all()
            question = question.prefetch_related(
                Prefetch('tag_set', queryset=qtags_qs, to_attr='tags'))
            if action != 'edit':
                raise Exception('Unsupported action')
            if question[0].author != user:
                raise Exception('Unauthorized action')
            return render(request, 'qa/edit_question.html',
                          {'question': question[0]})
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
                self._answer(request, question)
            elif action == 'edit':
                self._edit(request, question)
            elif action == 'comment':
                self._comment(request, question)
            elif action == 'append':
                self._append(request, question)
            elif action == 'delete':
                redirect_uri = '/'
                self._delete(request, question)
            elif action == 'upvote':
                self._vote(request, question)
            elif action == 'downvote':
                self._vote(request, question, False)
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

    def _edit(self, request, question):
        title = request.POST['title']
        content = request.POST['content']
        tags = request.POST['tags']
        err_msgs = []
        if not title:
            err_msgs.append('No title')
        if not content:
            err_msgs.append('No content')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        if request.user != question[0].author:
            raise Exception('Unauthorized action')
        question.update(
            title=title, content=content, updated_time=timezone.now())
        if tags:
            tags_list = parse_listed_strs(tags)
            stored_tags = set(
                question[0].tag_set.values_list('name', flat=True))
            inter = tags_list & stored_tags
            to_del = stored_tags - inter
            to_add = tags_list - inter
            for name in to_del:
                Tag.objects.filter(name=name, question=question[0]).delete()
            for name in to_add:
                Tag.objects.create(name=name, question=question[0]).save()

    def _comment(self, request, question):
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

    def _append(self, request, question):
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

    def _delete(self, request, question):
        if request.user != question[0].author:
            raise Exception('Unauthorized action')
        question.delete()

    def _vote(self, request, question, up=True):
        user = request.user
        voted = QuestionVote.objects.filter(question=question[0], user=user)
        if voted:
            if voted[0].vote_type != up:
                voted.delete()
        else:
            vote = QuestionVote.objects.create(
                question=question[0], user=user, vote_type=up)
            vote.save()

    def _answer(self, request, question):
        content = request.POST['answer_content']
        err_msgs = []
        if not content:
            err_msgs.append('No content')
        if err_msgs:
            raise InvalidFieldError(messages=err_msgs)
        # User is allowed to answer their questions
        # if request.user == question[0].author:
        # raise Exception('Unauthorized action')
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
            tags = request.POST['tags']
            user = request.user
            err_msgs = []
            if not title:
                err_msgs.append('No title')
            if not content:
                err_msgs.append('No content')
            if err_msgs:
                raise InvalidFieldError(messages=err_msgs)
            question = Question.objects.create(
                title=title, content=content, author=user)
            question.save()
            if tags:
                tags_list = parse_listed_strs(tags)
                for name in tags_list:
                    tag = Tag.objects.create(name=name, question=question)
                    tag.save()
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
        answer.update(content=content, updated_time=timezone.now())

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
        answer.update(accepted=True, accepted_time=timezone.now())
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


class EditAvatarView(View):

    @method_decorator(login_required)
    def get(self, request):
        tmp = str(request.user.member.avatar).split('.')
        avatar_path = tmp[0] + '_256_256.' + tmp[1]
        return render(request, 'qa/edit_avatar.html',
                      {'avatar_path': avatar_path})

    @method_decorator(login_required)
    def post(self, request):
        user = request.user

        try:
            # Use Clean Form?
            upload_image = request.FILES.get('image')
            if not upload_image:
                raise Http404

            # TODO: Check the uploaded file.
            user.member.avatar = upload_image
            user.member.save()

            return redirect('/profile/avatar/')
        except Exception as e:
            print(e)
            return redirect('/profile/avatar/')


class SearchView(View):

    def get(self, request):
        return render(request, 'qa/search.html')

    def post(self, request):
        try:
            search_type = request.POST.get('type')
            search_query = request.POST.get('query')
            # TODO: Split by space

            if not search_query:
                raise Http404

            if not search_type or search_type == 'question':
                search_type = 'question'
                result = search_question(search_query)

            elif search_type == 'user':
                result = search_user(search_query)

            else:
                raise Http404

            return render(request, 'qa/search.html', {'result': result,
                                                      'type': search_type})
        except Exception as e:
            print(e)
            return redirect('/search/')
