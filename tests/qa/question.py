#!/usr/bin/env python
#
# @name:  question.py
# @create: 25 September 2014 (Thursday)
# @update: 25 September 2014 (Thursday)
# @author: Z. Huang
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from Aristotle.apps.qa.models import Member


class AskQuestionTest(TestCase):

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user(
            username='test', password='test', email='test@test.com')
        Member.objects.create(user=user).save()

    def test_get_not_login(self):
        response = self.client.get('/question/ask/')
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        response = self.client.get('/question/ask/')
        self.assertEqual(response.status_code, 200)


class QuestionTest(TestCase):

    def setUp(self):
        self.client = Client()
        user1 = User.objects.create_user(
            username='test1', password='test', email='test1@test.com')
        Member.objects.create(user=user1).save()
        user2 = User.objects.create_user(
            username='test2', password='test', email='test2@test.com')
        Member.objects.create(user=user2).save()
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        question_data = {
            'title': 'test',
            'content': 'test content',
            'tags': 'test1, test2, test3',
        }
        self.client.post('/question/ask/', question_data)

    def test_get_not_login(self):
        response = self.client.get('/question/1/')
        self.assertEqual(response.status_code, 200)

    def test_get_owner_login(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/question/1/')
        self.assertEqual(response.status_code, 200)

    def test_get_login(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.get('/question/1/')
        self.assertEqual(response.status_code, 200)

    def test_get_not_exist(self):
        response = self.client.get('/question/1024/')
        self.assertEqual(response.status_code, 404)
