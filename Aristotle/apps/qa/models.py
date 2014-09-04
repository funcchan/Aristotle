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
    title = models.TextField(null=False)
    content = models.TextField(null=False)
    author = models.ForeignKey(User)
    number_of_views = models.IntegerField(default=0)
    solved = models.BooleanField(default=False)
    created_time = models.DateTimeField()
    # updated_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = timezone.now()
        return super(Question, self).save(*args, **kwargs)


class QuestionAppend(models.Model):
    question = models.ForeignKey(Question)
    content = models.TextField(null=False)
    created_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = timezone.now()
        return super(QuestionAppend, self).save(*args, **kwargs)


class QuestionComment(models.Model):
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    content = models.TextField(null=False)
    created_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = timezone.now()
        return super(QuestionComment, self).save(*args, **kwargs)


class QuestionVote(models.Model):
    question = models.ForeignKey(Question)
    user = models.ForeignKey(User)
    vote_type = models.BooleanField(default=False)
    reason = models.TextField()
    created_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = timezone.now()
        return super(QuestionVote, self).save(*args, **kwargs)


class Answer(models.Model):
    content = models.TextField(null=False)
    author = models.ForeignKey(User)
    question = models.ForeignKey(Question)
    up_votes = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)
    accepted = models.BooleanField(default=False)
    created_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = timezone.now()
        return super(Answer, self).save(*args, **kwargs)


class AnswerAppend(models.Model):
    answer = models.ForeignKey(Answer)
    content = models.TextField(null=False)
    created_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = timezone.now()
        return super(AnswerAppend, self).save(*args, **kwargs)


class AnswerComment(models.Model):
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(User)
    content = models.TextField(null=False)
    created_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = timezone.now()
        return super(AnswerComment, self).save(*args, **kwargs)


class AnswerVote(models.Model):
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(User)
    vote_type = models.BooleanField(default=False)
    reason = models.TextField()
    created_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_time = timezone.now()
        return super(AnswerVote, self).save(*args, **kwargs)


class Tag(models.Model):
    name = models.TextField(unique=True)
    question = models.ForeignKey(Question)
