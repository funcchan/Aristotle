#!/usr/bin/env python
#
# @name: models.py
# @create:
# @update: Sep. 4th, 2014
# @author:
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# class User(models.Model):
#     username = models.TextField(max_length=16)
#     password = models.TextField(max_length=16)
#     email = models.EmailField(unique=True)
#     first_name = models.TextField()
#     last_name = models.TextField()
#     gender = models.IntegerField()
#     age = models.IntegerField()
#     occupation = models.TextField(null=True)
#     education = models.TextField()
#     address = models.TextField(null=True)
#     phone = models.TextField(null=True)
#     company = models.TextField(null=True)
#     website = models.TextField(null=True)
#     avatar = models.TextField(null=True)
#     interests = models.TextField(null=True)
#     bio = models.TextField(null=True)
#     reg_time = models.DateTimeField()
#     last_login_time = models.DateTimeField()
#     last_login_ip = models.URLField()
#     level = models.IntegerField()
#     reputation = models.IntegerField()


class Question(models.Model):
    title = models.CharField(null=False, max_length=255)
    content = models.TextField(null=False)
    author = models.ForeignKey(User)
    solved = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=timezone.now())
    updated_time = models.DateTimeField(null=True)

    def _get_votes_count(self):
        return self.questionvote_set.all().count()

    def _get_answers_count(self):
        return self.answer_set.all().count()

    def _get_hits_count(self):
        return self.questionhit_set.all().count()

    votes_count = property(_get_votes_count)
    answers_count = property(_get_answers_count)
    hits_count = property(_get_hits_count)


class QuestionHit(models.Model):
    question = models.ForeignKey(Question)
    ip = models.CharField(null=False, max_length=40)
    session = models.CharField(null=False, max_length=120)
    created_time = models.DateTimeField(default=timezone.now())


class QuestionAppend(models.Model):
    question = models.ForeignKey(Question)
    content = models.TextField(null=False)
    created_time = models.DateTimeField(default=timezone.now())


class QuestionComment(models.Model):
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    content = models.TextField(null=False)
    created_time = models.DateTimeField(default=timezone.now())


class QuestionVote(models.Model):
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    vote_type = models.BooleanField(default=False)
    reason = models.CharField(max_length=255)
    created_time = models.DateTimeField(default=timezone.now())


class Answer(models.Model):
    content = models.TextField(null=False)
    author = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    accepted = models.BooleanField(default=False)
    accepted_time = models.DateTimeField(null=True)
    updated_time = models.DateTimeField(null=True)
    created_time = models.DateTimeField(default=timezone.now())


class AnswerAppend(models.Model):
    answer = models.ForeignKey(Answer)
    content = models.TextField(null=False)
    created_time = models.DateTimeField(default=timezone.now())


class AnswerComment(models.Model):
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(User)
    content = models.TextField(null=False)
    created_time = models.DateTimeField(default=timezone.now())


class AnswerVote(models.Model):
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(User)
    vote_type = models.BooleanField(default=False)
    reason = models.CharField(max_length=255)
    created_time = models.DateTimeField(default=timezone.now())


class Tag(models.Model):
    name = models.CharField(null=False, max_length=40)
    question = models.ForeignKey(Question)
