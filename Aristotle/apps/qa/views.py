#!/usr/bin/env python
#
# @name: views.py
# @create: Aug. 25th, 2014
# @update: Sep. 12th, 2014
# @author: Z. Huang, Liangju
import logging
from django.http import Http404, HttpResponse
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
from forms import ResetForm, ResetPasswordForm
from forms import EditProfileForm, EditAccountForm
from forms import EditAvatarForm, AskQuestionForm
from forms import EditQuestionForm, AnswerForm
from forms import CommentQuestionForm, AppendQuestionForm
from forms import EditAnswerForm, CommentAnswerForm
from forms import AppendAnswerForm
from notification import EmailNotification
from utils import parse_listed_strs

_DEFAULT_AVATAR = 'defaultavatar.jpg'
_HOME_PAGE_SIZE = 25
_TAG_PAGE_SIZE = 50
_USER_PAGE_SIZE = 50
_QUESTION_PAGE_SIZE = 25
_ANSWER_PAGE_SIZE = 25
logger = logging.getLogger(__name__)


def form_errors_handler(request, form, refer_url):
    for field, errors in form.errors.items():
        for error in errors:
            msg = '%s: %s' % (field, error)
            messages.error(request, msg)
    return redirect(refer_url)


class HomeView(View):

    def get(self, request, *args, **kwargs):
        """Home page
        """
        limit = _HOME_PAGE_SIZE
        questions = Question.objects.order_by('-created_time')[:limit]
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
            return form_errors_handler(request, form, refer_url)


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
            return form_errors_handler(request, form, refer_url)


class ActivateView(View):

    def get(self, request, *args, **kwargs):
        """Active user's account with a random code
        To verify the activation code, query from the
        Activation table with the code in URL
        if the code is valid (exists and not expire)
        then render the activation page
        otherwise send error messages
        """
        if kwargs and 'activation_code' in kwargs:
            code = kwargs['activation_code']
            try:
                result = Activation.objects.get(code=code)
                valid = not result.is_active
                valid = valid and result.expire_time > timezone.now()
                if valid:
                    result.is_active = True
                    result.save()
                    return render(request, 'qa/activation.html',
                                  {'valid': valid})
                else:
                    msg = 'The activation code has expired'
                    raise Exception(msg)
            except Exception as e:
                messages.error(request, str(e))
                # TODO
                # we need another page to show errors
                return redirect('/activate/')
        else:
            return render(request, 'qa/activation.html')


class ResetPasswordView(View):

    def get(self, request, *args, **kwargs):
        """Reset password
        reset.html is to ask user to input his/her email address
        reset_password.html is to set a new password with a random
        code sent to the user's email account
        if the code does not exist or has expired,
        then raise http 404
        """
        if kwargs and 'reset_code' in kwargs:
            code = kwargs['reset_code']
            result = ResetPassword.objects.filter(code=code)
            if not result or result[0].expire_time < timezone.now():
                raise Http404()
            form = ResetPasswordForm()
            return render(request, 'qa/reset_password.html',
                          {'form': form, 'code': code})
        else:
            form = ResetForm()
            return render(request, 'qa/reset.html', {'form': form})

    def post(self, request, *args, **kwargs):
        """Reset password actions
        reset: accept email address then send an email with a random
        link (it has expire time, 10mins). It will delete an existed
        code, may cause some safty issues

        User clicks the link and goes to reset_password page, input
        the new password twice to update.Only valid code can be used
        to update a user's password. After updating the password, the
        code will be deleted.
        """
        refer_url = request.META.get('HTTP_REFERER')
        try:
            if kwargs and 'reset_code' in kwargs:
                code = kwargs['reset_code']
                password = request.POST.get('password')
                form = ResetPasswordForm(request.POST)
                if form.is_valid():
                    result = ResetPassword.objects.get(code=code)
                    if result.expire_time > timezone.now():
                        result.user.set_password(password)
                        result.user.save()
                        result.delete()
                        return redirect('/signin/')
                    else:
                        msg = 'The code has expired'
                        raise Exception(msg)
                else:
                    return form_errors_handler(request, form, refer_url)
            else:
                email = request.POST.get('email')
                form = ResetForm(request.POST)
                if form.is_valid():
                    user = User.objects.get(email=email)
                    # TODO Email queue
                    EmailNotification(user).send_reset_password()
                    msg = 'please check your email to retrieve a reset link'
                    messages.success(request, msg)
                    return redirect('/reset/')
                else:
                    return form_errors_handler(request, form, refer_url)
        except Exception as e:
            messages.error(request, str(e))
            return redirect(refer_url)


class SignOutView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """logout using django auth
        """
        logout(request)
        return redirect('/signin/')


class ProfileView(View):

    def get(self, request, *args, **kwargs):
        """user profile page
        two url pattern:
        /profile/
        /profile/:id/
        if the user id does not exist or the user
        is a guest, then raise 404 error
        """
        if kwargs and 'user_id' in kwargs:
            uid = kwargs['user_id']
            try:
                user = User.objects.get(id=int(uid))
            except Exception:
                raise Http404()
        else:
            user = request.user
            if user.is_anonymous():
                raise Http404()
        questions = Question.objects.order_by(
            '-created_time').filter(author=user)
        answers = Answer.objects.order_by(
            '-created_time').filter(author=user)
        return render(request, 'qa/profile.html',
                      {'user': user,
                       'questions': questions,
                       'answers': answers})


class EditProfileView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """Edit profile page
        /profile/:id/edit/
        /profile/edit/
        """
        if kwargs and 'user_id' in kwargs:
            uid = kwargs['user_id']
            try:
                user = User.objects.get(id=int(uid))
            except Exception:
                raise Http404()
            if user != request.user:
                return HttpResponse(status=401)
        else:
            user = request.user
        member = user.member
        initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': member.age,
            'gender': member.gender,
            'occupation': member.occupation,
            'education': member.education,
            'address': member.address,
            'phone': member.phone,
            'company': member.company,
            'website': member.website,
            'interests': member.interests,
            'bio': member.bio,
        }
        form = EditProfileForm(initial=initial)
        return render(request, 'qa/edit_profile.html',
                      {'user': user, 'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """Edit user's profile
        Basic information of a user
        """
        if kwargs and 'user_id' in kwargs:
            uid = kwargs['user_id']
            try:
                user = User.objects.get(id=int(uid))
            except Exception:
                raise Http404()
            if user != request.user:
                return HttpResponse(status=401)
        else:
            user = request.user

        refer_url = request.META.get('HTTP_REFERER')
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
        form = EditProfileForm(request.POST)

        if form.is_valid():
            try:
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
                return redirect(refer_url)
            except Exception as e:
                messages.error(request, str(e))
                return redirect(refer_url)
        else:
            return form_errors_handler(request, form, refer_url)


class EditAccountView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        """Edit account page
        """
        if kwargs and 'user_id' in kwargs:
            uid = kwargs['user_id']
            try:
                user = User.objects.get(id=int(uid))
            except Exception:
                raise Http404()
            if user != request.user:
                return HttpResponse(status=401)
        else:
            user = request.user
        initial = {
            'username': user.username,
            'email': user.email,
        }
        form = EditAccountForm(initial=initial)
        return render(request, 'qa/edit_account.html',
                      {'user': user, 'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """Edit account
        user needs to verify his/her account with
        password
        """
        if kwargs and 'user_id' in kwargs:
            uid = kwargs['user_id']
            try:
                user = User.objects.get(id=int(uid))
            except Exception:
                raise Http404()
            if user != request.user:
                return HttpResponse(status=401)
        else:
            user = request.user
        refer_url = request.META.get('HTTP_REFERER')
        password = request.POST.get('password')
        username = request.POST.get('username')
        email = request.POST.get('email')
        newpassword = request.POST.get('newpassword')
        form = EditAccountForm(request.POST)

        if form.is_valid():
            try:
                if newpassword:
                    if user.check_password(password):
                        user.set_password(newpassword)
                    else:
                        msg = 'Incorrect password'
                        raise Exception(msg)
                user.username = username
                user.email = email
                user.save()
                return redirect('/signout/')
            except Exception as e:
                messages.error(request, str(e))
                return redirect(refer_url)
        else:
            return form_errors_handler(request, form, refer_url)


class EditAvatarView(View):

    @method_decorator(login_required)
    def get(self, request):
        """user avatar page
        """
        try:
            tmp = str(request.user.member.avatar).split('.')
            avatar_path = tmp[0] + '_256_256.' + tmp[1]
        except Exception:
            avatar_path = _DEFAULT_AVATAR
        form = EditAvatarForm()
        return render(request, 'qa/edit_avatar.html',
                      {'avatar_path': avatar_path, 'form': form})

    @method_decorator(login_required)
    def post(self, request):
        """upload user avatar
        """
        user = request.user
        refer_url = request.META.get('HTTP_REFERER')
        form = EditAvatarForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                upload_avatar = request.FILES.get('avatar')
                if not upload_avatar:
                    raise Exception('Incorrect image')
                user.member.avatar = upload_avatar
                user.member.save_avatar()
                return redirect(refer_url)
            except Exception as e:
                messages.error(request, str(e))
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


class QuestionsView(View):

    def get(self, request, *args, **kwargs):
        """A list of questions
        """
        page = request.GET.get('page')
        sort = request.GET.get('sort')
        per_page = request.GET.get('pagesize') or _QUESTION_PAGE_SIZE
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

        paginator = Paginator(question_list, per_page)
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
            questions = paginator.page(1)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)

        return render(request, 'qa/questions.html', {"questions": questions})


class TaggedQuestionsView(View):

    def get(self, request, *args, **kwargs):
        """A list of tagged questions
        """
        tag = kwargs['tag_name']
        page = request.GET.get('page')
        sort = request.GET.get('sort')
        per_page = request.GET.get('pagesize') or _QUESTION_PAGE_SIZE
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

        paginator = Paginator(question_list, per_page)
        try:
            questions = paginator.page(page)
        except PageNotAnInteger:
            questions = paginator.page(1)
        except EmptyPage:
            questions = paginator.page(paginator.num_pages)

        return render(request, 'qa/questions.html', {"questions": questions})


class TagsView(View):

    def get(self, request, *args, **kwargs):
        """A list of tags
        """
        page = request.GET.get('page')
        per_page = request.GET.get('pagesize') or _TAG_PAGE_SIZE
        tag_list = Tag.objects.values('name').distinct()
        paginator = Paginator(tag_list, per_page)
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
            return HttpResponse(status=401)

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
        refer_url = request.META.get('HTTP_REFERER')
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
                return HttpResponse(status=401)
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
                return HttpResponse(status=401)
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
            return HttpResponse(status=401)
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
        refer_url = request.META.get('HTTP_REFERER')
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
                return HttpResponse(status=401)
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
        refer_url = request.META['HTTP_REFERER']
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
            return HttpResponse(status=401)
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
            return HttpResponse(status=401)
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
            return HttpResponse(status=401)

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
            return HttpResponse(status=401)
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


class SearchView(View):

    def get(self, request, *args, **kwargs):
        """Search page
        """
        return render(request, 'qa/search.html')

    def post(self, request, *args, **kwargs):
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
            logger.error(str(e))
            return redirect('/search/')
