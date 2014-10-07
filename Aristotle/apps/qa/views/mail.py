#!/usr/bin/env python
#
# @name: mail.py
# @create: 06 October 2014 (Monday)
# @update: 06 October 2014 (Monday)
# @author: Z. Huang
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Aristotle.apps.qa.utils import form_errors_handler
import Aristotle.apps.qa.settings as qa_settings

logger = logging.getLogger(__name__)


class MailsView(View):

    def get(self, request, *args, **kwargs):
        pass


class MailView(View):

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass
