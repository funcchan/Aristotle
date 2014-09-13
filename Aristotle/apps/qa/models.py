#!/usr/bin/env python
#
# @name: models.py
# @create:
# @update: Sep. 12th, 2014
# @author:
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from PIL import Image
from settings import DEFAULT_AVATAR, AVATAR_PATH
from utils import get_utc_timestamp, format_time_path
from utils import get_utc_time


def upload_to_handler(instance, filename):
    tmp = filename.split('.')
    if tmp and len(tmp) == 2:
        path = format_time_path(AVATAR_PATH)
        # add random strings
        path += str(get_utc_timestamp()) + '.' + tmp[1]
        return path
    return DEFAULT_AVATAR


class Member(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'), ('Female', 'Female'), ('Unknown', 'Unknown')
    )
    user = models.OneToOneField(User)
    gender = models.CharField(
        default='Unknown', choices=GENDER_CHOICES, max_length=40)
    age = models.IntegerField(blank=True, default=0)
    occupation = models.CharField(blank=True, default='', max_length=100)
    education = models.CharField(blank=True, default='', max_length=20)
    address = models.CharField(blank=True, default='', max_length=255)
    phone = models.CharField(blank=True, default='', max_length=20)
    company = models.CharField(blank=True, default='', max_length=100)
    website = models.URLField(blank=True, default='')
    avatar = models.ImageField(blank=True, default=DEFAULT_AVATAR,
                               upload_to=upload_to_handler)
    interests = models.CharField(blank=True, default='', max_length=255)
    bio = models.TextField(blank=True)
    last_login_ip = models.CharField(blank=True, default='', max_length=40)

    def save_avatar(self, *args, **kwargs):
        """rewrite model's save method
        """
        if not self.id:
            return self.update()
        self.update()
        idx = self.avatar.path.find(AVATAR_PATH)
        prefix = self.avatar.path[0:idx]
        filename = self.avatar.path[idx+len(AVATAR_PATH):]
        avatar = Image.open(self.avatar).convert('RGB')
        size_list = {
            'large': (256, 256),
            'medium': (128, 128),
            'small': (32, 32),
        }

        for key, size in size_list.items():
            copy = avatar.copy()
            copy.thumbnail(size, Image.ANTIALIAS)
            new_path = ''.join([prefix, AVATAR_PATH, key, '/', filename])
            copy.save(new_path)
            copy.close()
        avatar.close()
        self.avatar.name = filename
        self.update()

    def update(self, *args, **kwargs):
        return super(Member, self).save(*args, **kwargs)


# class Preference(models.Model):
#     user = models.OneToOneField(User)
# notifications (w/ email)
# e.g.

# class Privacy(models.Model):
#     user = models.OneToOneField(User)

class Activation(models.Model):
    user = models.OneToOneField(User)
    is_active = models.BooleanField(default=False)
    code = models.CharField(
        unique=True, blank=True, default='', max_length=128)
    expire_time = models.DateTimeField(default=get_utc_time(3600))


class ResetPassword(models.Model):
    user = models.OneToOneField(User)
    code = models.CharField(
        unique=True, blank=True, default='', max_length=128)
    expire_time = models.DateTimeField(default=get_utc_time(600))


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

    def get_tags(self):
        return self.tag_set.all()

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

    def _get_votes_count(self):
        return self.answervote_set.all().count()

    def _get_abs_votes_count(self):
        ups = self.answervote_set.filter(vote_type=True).count()
        downs = self.votes_count - ups
        return ups - downs

    votes_count = property(_get_votes_count)
    abs_votes_count = property(_get_abs_votes_count)


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
