#!/usr/bin/env python
#
# @name:  question.py
# @create: 25 September 2014 (Thursday)
# @update: 26 September 2014 (Thursday)
# @author: Z. Huang
from django.test import TestCase
from django.test import Client


class AskQuestionTest(TestCase):

    def setUp(self):
        self.client = Client()
        data = {'username': 'test',
                'email': 'test@gmail.com',
                'password': 'test',
                'repassword': 'test'}
        self.client.post('/signup/', data)

    def test_get_not_login(self):
        response = self.client.get('/question/ask/')
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        response = self.client.get('/question/ask/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        pass


class QuestionTest(TestCase):

    def setUp(self):
        self.client = Client()
        user1_data = {'username': 'test1',
                      'email': 'test1@test.com',
                      'password': 'test',
                      'repassword': 'test'}
        self.client.post('/signup/', user1_data)
        user2_data = {'username': 'test2',
                      'email': 'test2@test.com',
                      'password': 'test',
                      'repassword': 'test'}
        self.client.post('/signup/', user2_data)
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


class QuestionActionTest(TestCase):

    def setUp(self):
        self.client = Client()
        user1_data = {'username': 'test1',
                      'email': 'test1@test.com',
                      'password': 'test',
                      'repassword': 'test'}
        self.client.post('/signup/', user1_data)
        user2_data = {'username': 'test2',
                      'email': 'test2@test.com',
                      'password': 'test',
                      'repassword': 'test'}
        self.client.post('/signup/', user2_data)
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        question_data = {
            'title': 'test',
            'content': 'test content',
            'tags': 'test1, test2, test3',
        }
        self.client.post('/question/ask/', question_data)
        self.client.get('/signout/')

    def test_get_not_login(self):
        response = self.client.get('/question/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_get_not_exist(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/question/2/edit/')
        self.assertEqual(response.status_code, 404)

    def test_get_not_auth(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.get('/question/1/edit/')
        self.assertEqual(response.status_code, 403)

    def test_get_not_edit_action(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/question/1/append/')
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/question/1/edit/')
        self.assertEqual(response.status_code, 200)
        # TODO test form contents

    def test_post_not_login(self):
        pass

    def test_post_not_exist(self):
        pass

    def test_post_not_auth(self):
        pass

    def test_post_edit(self):
        pass

    def test_post_comment(self):
        pass

    def test_post_append(self):
        pass

    def test_post_delete(self):
        pass

    def test_post_answer(self):
        pass

    def test_post_vote(self):
        pass


class AnswerActionTest(TestCase):

    def setUp(self):
        self.client = Client()
        user1_data = {'username': 'test1',
                      'email': 'test1@test.com',
                      'password': 'test',
                      'repassword': 'test'}
        self.client.post('/signup/', user1_data)
        user2_data = {'username': 'test2',
                      'email': 'test2@test.com',
                      'password': 'test',
                      'repassword': 'test'}
        self.client.post('/signup/', user2_data)
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        question_data = {
            'title': 'test',
            'content': 'test content',
            'tags': 'test1, test2, test3',
        }
        self.client.post('/question/ask/', question_data)
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        answer_data = {
            'content': 'test answer 1',
        }
        self.client.post('/question/1/answer', answer_data)
        self.client.get('/signout/')
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        answer_data = {
            'content': 'test answer 2',
        }
        self.client.post('/question/1/answer', answer_data)
        self.client.get('/signout/')

    def test_get_not_login(self):
        pass

    def test_get_not_exist(self):
        pass

    def test_get_not_auth(self):
        pass

    def test_get_not_edit_action(self):
        pass

    def test_get(self):
        pass

    def test_post_not_login(self):
        pass

    def test_post_not_exist(self):
        pass

    def test_post_not_auth(self):
        pass

    def test_post_edit(self):
        pass

    def test_post_comment(self):
        pass

    def test_post_append(self):
        pass

    def test_post_delete(self):
        pass

    def test_post_vote(self):
        pass

    def test_post_accept(self):
        pass
