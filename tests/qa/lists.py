#!/usr/bin/env python
#
# @name:  lists.py
# @create: 28 September 2014 (Sunday)
# @update: 30 September 2014 (Sunday)
# @author: Z. Huang

from django.test import TestCase
from django.test import Client
import Aristotle.apps.qa.settings as qa_settings


QUESTION_NUM = 30


class HomeTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        for i in range(QUESTION_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag1, tag2',
            }
            self.client.post('/question/ask/', question_data)
        self.client.get('/signout/')

    def test_get_not_login(self):
        self._test_home()

    def test_get(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        self._test_home()

    def _test_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        questions = response.context['questions']
        self.assertEqual(len(questions), qa_settings.HOME_PAGE_SIZE)


class QuestionsTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        for i in range(QUESTION_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag1, tag2',
            }
            self.client.post('/question/ask/', question_data)
        self.client.get('/signout/')

    def test_get(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        self._test_questions()

    def test_get_not_login(self):
        self._test_questions()

    def _test_questions(self):
        response = self.client.get('/questions/')
        self.assertEqual(response.status_code, 200)
        questions = response.context['questions']
        self.assertEqual(len(questions), qa_settings.QUESTION_PAGE_SIZE)
        self._test_questions_handler()
        self._test_questions_handler(5)
        self._test_questions_handler(10)
        self._test_questions_handler(20)
        self._test_questions_handler(30)
        self._test_questions_handler(50)

    def _test_questions_handler(self, page_size=None):
        if not page_size:
            page_size = qa_settings.QUESTION_PAGE_SIZE
            url = '/questions/?page={0}'
        else:
            url = '/questions/?page={0}&pagesize=' + str(page_size)
        pages = QUESTION_NUM / page_size
        pages += 1 if QUESTION_NUM % page_size != 0 else 0
        for i in range(1, pages + 1):
            response = self.client.get(url.format(i))
            self.assertEqual(response.status_code, 200)
            questions = response.context['questions']
            if i == pages:
                size = QUESTION_NUM - (i - 1) * page_size
            else:
                size = page_size
            self.assertEqual(len(questions), size)


class TaggedQuestionsTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)


class TagsTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)


class UsersTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)

    def test_get(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)

    def test_get_not_login(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)
