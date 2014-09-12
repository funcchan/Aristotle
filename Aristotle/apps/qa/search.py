#!/usr/bin/env python
#
# @name: views.py
# @create: Sep. 11th, 2014
# @update: Sep. 11th, 2014
# @author: Liangju Li
from django.contrib.auth.models import User
from django.db.models import Q
from Aristotle.apps.qa.models import Question


def search_question(query):
        # TODO: This is just a raw search. We should add more features here.
        results = Question.objects.filter(Q(content__contains=query)
                                          | Q(title__contains=query))
        return results


def search_user(query):
    results_user = User.objects.filter(username__contains=query)
    return results_user
