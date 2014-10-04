#!/usr/bin/env python
#
# @name: search.py
# @create: Sep. 11th, 2014
# @update: 04 October 2014 (Saturday)
# @author: Liangju Li, Z. Huang
from django.contrib.auth.models import User
from django.db.models import Q
from Aristotle.apps.qa.models import Question


class Search(object):
    '''interface for the searching engine
    '''

    def __init__(self, query):
        self.query = query

    def questions(self):
        question_filter = Q(content__contains=self.query) | Q(
            title__contains=self.query)
        results = Question.objects.filter(question_filter)
        return results

    def users(self):
        results = User.objects.filter(username__contains=self.query)
        return results

    def tags(self):
        pass

    def related_questions(self):
        pass

    def related_tags(self):
        pass

    def related_users(self):
        pass

    def newest_questions(self):
        pass

    def hotest_questions(self):
        pass
