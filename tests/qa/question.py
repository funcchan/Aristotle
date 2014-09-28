#!/usr/bin/env python
#
# @name:  question.py
# @create: 25 September 2014 (Thursday)
# @update: 27 September 2014 (Thursday)
# @author: Z. Huang
from django.test import TestCase
from django.test import Client
from Aristotle.apps.qa.models import Question


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
        response = self.client.get('/question/3/edit/')
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
        response = self.client.post('/question/1/edit/', {})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/question/1/answer/', {})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/question/1/comment/', {})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/question/1/append/', {})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/question/1/delete/', {})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/question/1/upvote/', {})
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/question/1/downvote/', {})
        self.assertEqual(response.status_code, 302)

    def test_post_not_exist(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.post('/question/3/edit/', {})
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/question/323/answer/', {})
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/question/5123/comment/', {})
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/question/7as/append/', {})
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/question/8123/delete/', {})
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/question/a/upvote/', {})
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/question/fake/downvote/', {})
        self.assertEqual(response.status_code, 404)

    def test_post_not_auth_edit(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'title': 'testing of editing title',
            'content': 'new contents',
            'tags': 'test1, test3, test5'
        }
        response = self.client.post('/question/1/edit/', data)
        self.assertEqual(response.status_code, 403)

    def test_post_not_auth_append(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'question_append_content': 'appended contents',
        }
        response = self.client.post('/question/1/append/', data)
        self.assertEqual(response.status_code, 403)

    def test_post_not_auth_delete(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.post('/question/1/delete/')
        self.assertEqual(response.status_code, 403)

    def test_post_edit(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'title': 'testing of editing title',
            'content': 'new contents',
            'tags': 'test1, test3, test5'
        }
        question = Question.objects.get(id=1)
        self.assertEqual(question.title, 'test')
        self.assertEqual(question.content, 'test content')
        response = self.client.post('/question/1/edit/', data)
        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(id=1)
        self.assertEqual(question.title, 'testing of editing title')
        self.assertEqual(question.content, 'new contents')

    def test_post_append(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'question_append_content': 'appended contents'
        }
        append = Question.objects.get(id=1).questionappend_set.first()
        self.assertIsNone(append)
        response = self.client.post('/question/1/append/', data)
        self.assertEqual(response.status_code, 302)
        append = Question.objects.get(id=1).questionappend_set.first()
        self.assertIsNotNone(append)
        self.assertEqual(append.content, 'appended contents')

    def test_post_comment(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'question_comment_content': 'comment 1'
        }
        comment = Question.objects.get(id=1).questioncomment_set.first()
        self.assertIsNone(comment)
        response = self.client.post('/question/1/comment/', data)
        self.assertEqual(response.status_code, 302)
        comment = Question.objects.get(id=1).questioncomment_set.first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.content, 'comment 1')
        self.assertEqual(comment.user.username, 'test1')
        self.client.get('/signout/')
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'question_comment_content': 'comment 2'
        }
        response = self.client.post('/question/1/comment/', data)
        comment = Question.objects.get(id=1).questioncomment_set.all()[1]
        self.assertEqual(comment.content, 'comment 2')
        self.assertEqual(comment.user.username, 'test2')

    def test_post_answer(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'answer_content': 'answer 1'
        }
        answer = Question.objects.get(id=1).answer_set.first()
        self.assertIsNone(answer)
        response = self.client.post('/question/1/answer/', data)
        self.assertEqual(response.status_code, 302)
        answer = Question.objects.get(id=1).answer_set.first()
        self.assertIsNotNone(answer)
        self.assertEqual(answer.content, 'answer 1')
        self.assertEqual(answer.author.username, 'test2')
        self.client.get('/signout/')
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'answer_content': 'answer 2'
        }
        response = self.client.post('/question/1/answer/', data)
        answer = Question.objects.get(id=1).answer_set.all()[1]
        self.assertEqual(answer.content, 'answer 2')
        self.assertEqual(answer.author.username, 'test1')

    def test_post_vote(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        vote = Question.objects.get(id=1).questionvote_set.first()
        self.assertIsNone(vote)
        response = self.client.post('/question/1/upvote/')
        self.assertEqual(response.status_code, 302)
        votes = Question.objects.get(id=1).questionvote_set.all()
        vote = votes[0]
        self.assertEqual(len(votes), 1)
        self.assertTrue(vote.vote_type)
        response = self.client.post('/question/1/upvote/')
        self.assertEqual(response.status_code, 302)
        votes = Question.objects.get(id=1).questionvote_set.all()
        self.assertEqual(len(votes), 1)
        response = self.client.post('/question/1/downvote/')
        self.assertEqual(response.status_code, 302)
        vote = Question.objects.get(id=1).questionvote_set.first()
        self.assertIsNone(vote)
        self.client.get('/signout/')
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.post('/question/1/upvote/')
        self.assertEqual(response.status_code, 302)
        vote = Question.objects.get(id=1).questionvote_set.first()
        self.assertIsNone(vote)

    def test_post_delete(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.post('/question/1/delete/')
        self.assertEqual(response.status_code, 302)
        question = Question.objects.filter(id=1).first()
        self.assertIsNone(question)


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
