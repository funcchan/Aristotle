#!/usr/bin/env python
#
# @name:  lists.py
# @create: 28 September 2014 (Sunday)
# @update: 29 September 2014 (Sunday)
# @author: Z. Huang

from django.test import TestCase
from django.test import Client

QUESTION_NUM = 30


class HomeTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)

        for i in range(QUESTION_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag1, tag2',
            }
            self.client.post('/question/ask/', question_data)

    def test_get_not_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class QuestionsTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)

        for i in range(QUESTION_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag1, tag2',
            }
            self.client.post('/question/ask/', question_data)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        response = self.client.get('/questions/')
        self.assertEqual(response.status_code, 200)

    def test_get_not_login(self):
        response = self.client.get('/questions/')
        self.assertEqual(response.status_code, 200)


class TaggedQuestionsTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)

        for i in range(QUESTION_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag1, tag2',
            }
            self.client.post('/question/ask/', question_data)

    def test_get(self):
        pass

    def test_get_not_login(self):
        pass


class TagsTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)

        for i in range(QUESTION_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag1, tag2',
            }
            self.client.post('/question/ask/', question_data)

    def test_get(self):
        pass

    def test_get_not_login(self):
        pass


class UsersTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)

    def test_get(self):
        pass

    def test_get_not_login(self):
        pass
