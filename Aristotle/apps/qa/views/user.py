#!/usr/bin/env python
#
# @name:  user.py
# @create: 24 September 2014 (Wednesday)
# @update: 02 October 2014 (Thursday)
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

from Aristotle.apps.qa.models import Question, Answer
from Aristotle.apps.qa.models import Member, Activation
from Aristotle.apps.qa.models import ResetPassword
from Aristotle.apps.qa.forms import SignInForm, SignUpForm
from Aristotle.apps.qa.forms import ResetForm, ResetPasswordForm
from Aristotle.apps.qa.forms import EditProfileForm, EditAccountForm
from Aristotle.apps.qa.forms import EditAvatarForm
from Aristotle.apps.qa.notification import EmailNotification
from Aristotle.apps.qa.utils import form_errors_handler
import Aristotle.apps.qa.settings as qa_settings

logger = logging.getLogger(__name__)


class SignInView(View):

    def get(self, request, *args, **kwargs):
        """render login page
        if user has logged in, redirect back to referer page or home page
        """
        if request.user.is_authenticated():
            ref = request.META.get('HTTP_REFERER') or '/'
            return redirect(ref)
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
        next_url = request.POST.get('next') or '/'
        refer_url = request.META.get('HTTP_REFERER') or '/'
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                ip = request.META['REMOTE_ADDR']
                login(request, user)
                Member.objects.filter(user=user).update(last_login_ip=ip)
                return redirect(next_url)
            else:
                msg = 'username and/or password is not correct'
                messages.error(request, msg)
                logger.error(msg)
                return redirect(refer_url)
        else:
            return form_errors_handler(request, form, refer_url)


class SignUpView(View):

    def get(self, request, *args, **kwargs):
        """render sign up page
        if user has logged in, redirect back to referer page or home page
        """
        if request.user.is_authenticated():
            ref = request.META.get('HTTP_REFERER') or '/'
            return redirect(ref)
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
        refer_url = request.META.get('HTTP_REFERER') or '/'
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
                logger.error(str(e))
                messages.error(request, str(e))
                return redirect(refer_url)
        else:
            return form_errors_handler(request, form, refer_url)


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
                logger.error('user does not exist')
                raise Http404()
        else:
            user = request.user
            if user.is_anonymous():
                logger.error('not authenticated')
                return HttpResponse(status=403)
        questions = Question.objects.order_by(
            '-created_time').filter(author=user)
        answers = Answer.objects.order_by(
            '-created_time').filter(author=user)

        if user.member and user.member.avatar:
            avatar = str(user.member.avatar)
        else:
            avatar = qa_settings.DEFAULT_AVATAR
        avatar_path = qa_settings.AVATAR_PATH + 'large/' + avatar

        return render(request, 'qa/profile.html',
                      {'user': user,
                       'questions': questions,
                       'answers': answers,
                       'avatar_path': avatar_path})


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
                logger.error('user does not exist')
                raise Http404()
            if user != request.user:
                logger.error('not authenticated')
                return HttpResponse(status=403)
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
                logger.error('user does not exist')
                raise Http404()
            if user != request.user:
                logger.error('not authenticated')
                return HttpResponse(status=403)
        else:
            user = request.user

        refer_url = request.META.get('HTTP_REFERER') or '/'
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        age = request.POST.get('age') or 0
        gender = request.POST.get('gender') or 'Unknown'
        occupation = request.POST.get('occupation') or ''
        education = request.POST.get('education') or ''
        address = request.POST.get('address') or ''
        phone = request.POST.get('phone') or ''
        company = request.POST.get('company') or ''
        website = request.POST.get('website') or ''
        interests = request.POST.get('interests') or ''
        bio = request.POST.get('bio') or ''
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
                logger.error(str(e))
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
                logger.error('user does not exist')
                raise Http404()
            if user != request.user:
                logger.error('not authenticated')
                return HttpResponse(status=403)
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
                logger.error('user does not exist')
                raise Http404()
            if user != request.user:
                logger.error('not authenticated')
                return HttpResponse(status=403)
        else:
            user = request.user
        refer_url = request.META.get('HTTP_REFERER') or '/'
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
                logger.error(str(e))
                messages.error(request, str(e))
                return redirect(refer_url)
        else:
            return form_errors_handler(request, form, refer_url)


class EditAvatarView(View):

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        """user avatar page
        """

        if kwargs and 'user_id' in kwargs:
            uid = kwargs['user_id']
            try:
                user = User.objects.get(id=int(uid))
            except Exception:
                logger.error('user does not exist')
                raise Http404()
            if user != request.user:
                logger.error('not authenticated')
                return HttpResponse(status=403)
        else:
            user = request.user

        if user.member.avatar:
            avatar = str(user.member.avatar)
        else:
            avatar = qa_settings.DEFAULT_AVATAR
        avatar_path = qa_settings.AVATAR_PATH + 'large/' + avatar
        form = EditAvatarForm()
        return render(request, 'qa/edit_avatar.html',
                      {'avatar_path': avatar_path, 'form': form})

    @method_decorator(login_required)
    def post(self, request, **kwargs):
        """upload user avatar
        """
        if kwargs and 'user_id' in kwargs:
            uid = kwargs['user_id']
            try:
                user = User.objects.get(id=int(uid))
            except Exception:
                logger.error('user does not exist')
                raise Http404()
            if user != request.user:
                logger.error('not authenticated')
                return HttpResponse(status=403)
        else:
            user = request.user

        refer_url = request.META.get('HTTP_REFERER') or '/'
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
                logger.error(str(e))
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
                    msg = 'The activation code is not valid or has expired'
                    raise Exception(msg)
            except Exception as e:
                logger.error(str(e))
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
                logger.error('code does not exist or has expired')
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
        refer_url = request.META.get('HTTP_REFERER') or '/'
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
            logger.error(str(e))
            messages.error(request, str(e))
            return redirect(refer_url)
