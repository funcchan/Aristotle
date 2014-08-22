from django.db import models

# Create your models here.
class User(models.Model):
    # id = models.TextField(primary_key=True)
    username = models.TextField(max_length=16)
    pwd = models.TextField(max_length=16)
    email = models.EmailField(unique=True)
    first_name = models.TextField()
    last_name = models.TextField()
    gender = models.IntegerField()
    age = models.IntegerField()
    occupation = models.TextField(null=True)
    education = models.TextField()
    address = models.TextField(null=True)
    phone = models.TextField(null=True)
    company = models.TextField(null=True)
    website = models.TextField(null=True)
    avatar = models.ImageField(null=True)
    interests = models.TextField(null=True)
    bio = models.TextField(null=True)
    reg_time = models.DateTimeField()
    last_login_time = models.DateTimeField()
    last_login_ip = models.URLField()
    level = models.IntegerField()
    reputation = models.IntegerField()

class Question(models.Model):
    # id = models.TextField(primary_key=True)
    title = models.TextField()
    content = models.TextField()
    author_id = models.ForeignKey('User')
    up_votes = models.IntegerField()
    down_votes = models.IntegerField()
    number_of_views = models.IntegerField()
    solved = models.BooleanField()

class QuestionAppend(models.Model):
    # id = models.TextField(primary_key=True)
    question_id = models.ForeignKey('Question')
    content = models.TextField()
    time = models.DateTimeField()

class QuestionComment(models.Model):
    # id = models.TextField(primary_key=True)
    question_id = models.ForeignKey('Question')
    user_id = models.ForeignKey('User')
    content = models.TextField()
    time = models.DateTimeField()

class QuestionVote(models.Model):
    # id = models.TextField(primary_key=True)
    question_id = models.ForeignKey('Question')
    user_id = models.ForeignKey('User')
    type = models.BooleanField()
    reason = models.TextField()
    time = models.DateTimeField()

class Answer(models.Model):
    # id = models.TextField(primary_key=True)
    content = models.TextField()
    author_id = models.ForeignKey('User')
    question_id = models.ForeignKey('Question')
    up_votes = models.IntegerField()
    down_votes = models.IntegerField()
    accepted = models.BooleanField()
    created_time = models.DateTimeField()

class AnswerAppend(models.Model):
    # id = models.TextField(primary_key=True)
    answer_id = models.ForeignKey('Answer')
    content = models.TextField()
    add_date = models.DateTimeField()

class AnswerComment(models.Model):
    # id = models.TextField(primary_key=True)
    answer_id = models.ForeignKey('Answer')
    user_id = models.ForeignKey('User')
    content = models.TextField()
    time = models.DateTimeField()

class AnswerVote(models.Model):
    # id = models.TextField(primary_key=True)
    answer_id = models.ForeignKey('Answer')
    user_id = models.ForeignKey('User')
    type = models.BooleanField()
    reason = models.TextField()
    time = models.DateTimeField()

class Tag(models.Model):
    # id = models.TextField(primary_key=True)
    name = models.TextField(unique=True)
    question_id = models.ForeignKey('Question')
