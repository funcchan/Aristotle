#!/usr/bin/env python
#
# @name:  lists.py
# @create: 28 September 2014 (Sunday)
# @update: 05 October 2014 (Sunday)
# @author: Z. Huang

from django.test import TestCase
from django.test import Client
import Aristotle.apps.qa.settings as qa_settings


QUESTION_NUM = 30
TAG_NUM = 60
USER_NUM = 60


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
        for i in range(0, 50, 10):
            self._test_questions_handler(i)

    def _test_questions_handler(self, page_size=None):
        if not page_size or page_size == 0:
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
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        for i in range(QUESTION_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag1',
            }
            self.client.post('/question/ask/', question_data)
        for i in range(QUESTION_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag2',
            }
            self.client.post('/question/ask/', question_data)
        self.client.get('/signout/')

    def test_get(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        self._test_questions()

    def test_get_not_login(self):
        self._test_questions()

    def _test_questions(self):
        response = self.client.get('/questions/tagged/tag1/')
        self.assertEqual(response.status_code, 200)
        questions = response.context['questions']
        self.assertEqual(len(questions), qa_settings.QUESTION_PAGE_SIZE)
        response = self.client.get('/questions/tagged/tag2/')
        self.assertEqual(response.status_code, 200)
        questions = response.context['questions']
        self.assertEqual(len(questions), qa_settings.QUESTION_PAGE_SIZE)
        self._test_questions_handler('tag1')
        for i in range(0, 50, 10):
            self._test_questions_handler('tag1', i)
        self._test_questions_handler('tag2')
        for i in range(0, 50, 10):
            self._test_questions_handler('tag2', i)

    def _test_questions_handler(self, tag, page_size=None):
        if not page_size or page_size == 0:
            page_size = qa_settings.QUESTION_PAGE_SIZE
            url = '/questions/tagged/' + tag + '/?page={0}'
        else:
            url = '/questions/tagged/' + tag + \
                '/?page={0}&pagesize=' + str(page_size)
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


class TagsTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        for i in range(TAG_NUM):
            question_data = {
                'title': 'title ' + str(i),
                'content': 'content ' + str(i),
                'tags': 'tag' + str(i),
            }
            self.client.post('/question/ask/', question_data)
        self.client.get('/signout/')

    def test_get(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        self._test_tags()

    def test_get_not_login(self):
        self._test_tags()

    def _test_tags(self):
        response = self.client.get('/tags/')
        self.assertEqual(response.status_code, 200)
        tags = response.context['tags']
        self.assertEqual(len(tags), qa_settings.TAG_PAGE_SIZE)
        self._test_tags_handler()
        for i in range(0, 70, 10):
            self._test_tags_handler(i)

    def _test_tags_handler(self, page_size=None):
        if not page_size or page_size == 0:
            page_size = qa_settings.TAG_PAGE_SIZE
            url = '/tags/?page={0}'
        else:
            url = '/tags/?page={0}&pagesize=' + str(page_size)
        pages = TAG_NUM / page_size
        pages += 1 if TAG_NUM % page_size != 0 else 0
        for i in range(1, pages + 1):
            response = self.client.get(url.format(i))
            self.assertEqual(response.status_code, 200)
            tags = response.context['tags']
            if i == pages:
                size = TAG_NUM - (i - 1) * page_size
            else:
                size = page_size
            self.assertEqual(len(tags), size)


class UsersTest(TestCase):

    def setUp(self):
        self.client = Client()
        for i in range(USER_NUM):
            user_data = {'username': 'test' + str(i),
                         'email': 'test' + str(i) + '@gmail.com',
                         'password': 'test',
                         'repassword': 'test'}
            self.client.post('/signup/', user_data)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test0', 'password': 'test'})
        self._test_users()

    def test_get_not_login(self):
        self._test_users()

    def _test_users(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, 200)
        users = response.context['users']
        self.assertEqual(len(users), qa_settings.USER_PAGE_SIZE)
        self._test_users_handler()
        for i in range(0, 70, 10):
            self._test_users_handler(i)

    def _test_users_handler(self, page_size=None):
        if not page_size or page_size == 0:
            page_size = qa_settings.USER_PAGE_SIZE
            url = '/users/?page={0}'
        else:
            url = '/users/?page={0}&pagesize=' + str(page_size)
        pages = USER_NUM / page_size
        pages += 1 if USER_NUM % page_size != 0 else 0
        for i in range(1, pages + 1):
            response = self.client.get(url.format(i))
            self.assertEqual(response.status_code, 200)
            users = response.context['users']
            if i == pages:
                size = USER_NUM - (i - 1) * page_size
            else:
                size = page_size
            self.assertEqual(len(users), size)


class SearchTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@gmail.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        for i in range(5):
            for j in range(QUESTION_NUM):
                question_data = {
                    'title': 'title ' + str(i + 1),
                    'content': 'content ' + str(i + 1),
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
        response = self.client.get('/search/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/search/?query=1')
        self.assertEqual(response.status_code, 200)
        questions = response.context['questions']
        self.assertEqual(len(questions), qa_settings.QUESTION_PAGE_SIZE)
        self._test_questions_handler('1')
        for i in range(5):
            for j in range(0, 50, 10):
                self._test_questions_handler(str(i + 1), j)

    def _test_questions_handler(self, query, page_size=None):
        if not page_size or page_size == 0:
            page_size = qa_settings.QUESTION_PAGE_SIZE
            url = '/search/?query=' + query + '&page={0}'
        else:
            url = '/search/?query=' + query + \
                '&page={0}&pagesize=' + str(page_size)
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
