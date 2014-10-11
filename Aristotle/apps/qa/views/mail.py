#!/usr/bin/env python
#
# @name: mail.py
# @create: 06 October 2014 (Monday)
# @update: 10 October 2014 (Friday)
# @author: Z. Huang
import logging
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Aristotle.apps.qa.forms import MailForm
from Aristotle.apps.qa.utils import form_errors_handler
from Aristotle.apps.qa.models import Mail
# import Aristotle.apps.qa.settings as qa_settings

logger = logging.getLogger(__name__)


class MailsView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        pass


class MailView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        pass

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        receiver_user = request.POST.get('receiver')
        sender = request.user
        user = sender
        refer_url = request.META.get('HTTP_REFERER') or '/'
        form = MailForm(request.POST)

        if form.is_valid():
            try:
                receiver = User.objects.get(username=receiver_user)
                send_mail = Mail.objects.create(
                    subject=subject, content=content,
                    user=user, has_read=True,
                    sender=sender, receiver=receiver)
                send_mail.save()
                receive_mail = Mail.objects.create(
                    subject=subject, content=content,
                    user=receiver,
                    sender=sender, receiver=receiver)
                receive_mail.save()
                # redirect to?
                return redirect('/mail/')
            except Exception as e:
                logger.error(str(e))
                messages.error(request, str(e))
                return redirect(refer_url)
        else:
            return form_errors_handler(request, form, refer_url)
