#!/usr/bin/env python
#
# @name: mail.py
# @create: 06 October 2014 (Monday)
# @update: 11 October 2014 (Saturday)
# @author: Z. Huang
import logging
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Aristotle.apps.qa.forms import MailForm
from Aristotle.apps.qa.utils import form_errors_handler
from Aristotle.apps.qa.models import Mail
from Aristotle.apps.qa.utils import parse_listed_strs
import Aristotle.apps.qa.settings as qa_settings

logger = logging.getLogger(__name__)


class MailsView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        user = request.user
        if 'box' in kwargs:
            box = kwargs['box']
        else:
            box = 'inbox'
        page = request.GET.get('page')
        per_page = request.GET.get('pagesize')
        if not per_page or per_page == '0' or per_page == 0:
            per_page = qa_settings.MAIL_PAGE_SIZE
        mail_list = Mail.objects.order_by(
            '-created_time').filter(user=user, box=box)
        paginator = Paginator(mail_list, per_page)
        try:
            mails = paginator.page(page)
        except PageNotAnInteger:
            mails = paginator.page(1)
        except EmptyPage:
            mails = paginator.page(paginator.num_pages)
        return render(request, 'qa/mails.html', {'mails': mails})


class MailView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        mid = kwargs['mail_id']
        user = request.user
        try:
            mid = int(mid)
        except TypeError:
            logger.error('mail does not exist')
            raise Http404()

        mail_queryset = Mail.objects.filter(id=mid, user=user)

        if not mail_queryset:
            logger.error('mail does not exist')
            raise Http404()

        mail = mail_queryset[0]
        data = {
            'mail': mail
        }
        return render(request, 'qa/mail.html', data)

    # @method_decorator(login_required)
    # def post(self, request, *args, **kwargs):
    #     pass


class SendMailView(View):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = MailForm()
        return render(request, 'qa/send_mail.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # action = kwargs['action']
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        receivers = request.POST.get('receivers')
        sender = request.user
        user = sender
        refer_url = request.META.get('HTTP_REFERER') or '/'
        form = MailForm(request.POST)

        if form.is_valid():
            try:
                receivers_list = parse_listed_strs(receivers)
                for username in receivers_list:
                    receiver = User.objects.get(username=username)
                    send_mail = Mail.objects.create(
                        subject=subject, content=content,
                        user=user, has_read=True, box='outbox',
                        sender=sender, receiver=receiver)
                    send_mail.save()
                    receive_mail = Mail.objects.create(
                        subject=subject, content=content,
                        user=receiver, box='inbox',
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
