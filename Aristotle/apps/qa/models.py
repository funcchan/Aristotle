#!/usr/bin/env python
#
# @name: models.py
# @create:
# @update:
# @author:
import datetime
from django.db import models
from django.contrib.auth.models import User

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
    title = models.TextField()
    content = models.TextField()
    author_id = models.ForeignKey(User)
    up_votes = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)
    number_of_views = models.IntegerField(default=0)
    solved = models.BooleanField(default=False)
    created_time = models.DateTimeField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id:
            self.created_time = datetime.datetime.today()
        super().save(force_insert, force_update, using, update_fields)


class QuestionAppend(models.Model):
    question_id = models.ForeignKey(Question)
    content = models.TextField()
    created_time = models.DateTimeField()


class QuestionComment(models.Model):
    question_id = models.ForeignKey(Question)
    user_id = models.ForeignKey(User)
    content = models.TextField()
    created_time = models.DateTimeField()


class QuestionVote(models.Model):
    question_id = models.ForeignKey(Question)
    user_id = models.ForeignKey(User)
    vote_type = models.BooleanField()
    reason = models.TextField()
    created_time = models.DateTimeField()


class Answer(models.Model):
    content = models.TextField()
    author_id = models.ForeignKey(User)
    question_id = models.ForeignKey(Question)
    up_votes = models.IntegerField()
    down_votes = models.IntegerField()
    accepted = models.BooleanField()
    created_time = models.DateTimeField()


class AnswerAppend(models.Model):
    answer_id = models.ForeignKey(Answer)
    content = models.TextField()
    created_time = models.DateTimeField()


class AnswerComment(models.Model):
    answer_id = models.ForeignKey(Answer)
    user_id = models.ForeignKey(User)
    content = models.TextField()
    created_time = models.DateTimeField()


class AnswerVote(models.Model):
    answer_id = models.ForeignKey(Answer)
    user_id = models.ForeignKey(User)
    vote_type = models.BooleanField()
    reason = models.TextField()
    created_time = models.DateTimeField()


# class Tag(models.Model):
#     name = models.TextField(unique=True)
#     question_id = models.ForeignKey(Question)
