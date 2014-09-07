#!/usr/bin/env python
#
# @name: models.py
# @create:
# @update: Sep. 7th, 2014
# @author:
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Member(models.Model):
    user = models.OneToOneField(User)
    gender = models.IntegerField(default=0)
    age = models.IntegerField(blank=True, default=0)
    occupation = models.CharField(blank=True, default='', max_length=100)
    education = models.CharField(blank=True, default='', max_length=20)
    address = models.CharField(blank=True, default='', max_length=255)
    phone = models.CharField(blank=True, default='', max_length=20)
    company = models.CharField(blank=True, default='', max_length=100)
    website = models.URLField(blank=True, default='')
    avatar = models.ImageField(blank=True, default='defaultavatar.jpg',
                               upload_to='uploads/avatars/%m-%Y/')
    interests = models.CharField(blank=True, default='', max_length=255)
    bio = models.TextField(blank=True)
    last_login_ip = models.CharField(blank=True, default='', max_length=40)
    # level = models.IntegerField()
    # reputation = models.IntegerField()


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User)
    solved = models.BooleanField(default=False)
    created_time = models.DateTimeField(default=timezone.now())
    updated_time = models.DateTimeField(blank=True, null=True)

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
    ip = models.CharField(max_length=40)
    session = models.CharField(max_length=120)
    created_time = models.DateTimeField(default=timezone.now())


class QuestionAppend(models.Model):
    question = models.ForeignKey(Question)
    content = models.TextField()
    created_time = models.DateTimeField(default=timezone.now())


class QuestionComment(models.Model):
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    content = models.TextField()
    created_time = models.DateTimeField(default=timezone.now())


class QuestionVote(models.Model):
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    vote_type = models.BooleanField(default=False)
    reason = models.CharField(max_length=255)
    created_time = models.DateTimeField(default=timezone.now())


class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    accepted = models.BooleanField(default=False)
    accepted_time = models.DateTimeField(blank=True, null=True)
    updated_time = models.DateTimeField(blank=True, null=True)
    created_time = models.DateTimeField(default=timezone.now())


class AnswerAppend(models.Model):
    answer = models.ForeignKey(Answer)
    content = models.TextField()
    created_time = models.DateTimeField(default=timezone.now())


class AnswerComment(models.Model):
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(User)
    content = models.TextField()
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
