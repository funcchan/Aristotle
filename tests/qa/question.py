#!/usr/bin/env python
#
# @name:  question.py
# @create: 25 September 2014 (Thursday)
# @update: 28 September 2014 (Thursday)
# @author: Z. Huang
from django.test import TestCase
from django.test import Client
from Aristotle.apps.qa.models import Question, Answer


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

    def test_post_not_login(self):
        response = self.client.post('/question/ask/', {})
        self.assertEqual(response.status_code, 302)

    def test_post(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        data = {
            'title': 'title',
            'content': 'content',
            'tags': 'tag1, tag2, tag3',
        }
        tags_data = set(['tag1', 'tag2', 'tag3'])
        test_tags_data = set()
        question = Question.objects.first()
        self.assertIsNone(question)
        response = self.client.post('/question/ask/', data)
        self.assertEqual(response.status_code, 302)
        # TODO test redirected URL
        question = Question.objects.first()
        self.assertIsNotNone(question)
        self.assertEqual(question.title, 'title')
        self.assertEqual(question.content, 'content')
        self.assertEqual(question.author.username, 'test')
        tags = question.tag_set.all()
        self.assertEqual(len(tags), 3)
        for tag in tags:
            test_tags_data.add(tag.name)
        self.assertSetEqual(test_tags_data, tags_data)


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
            'tags': 'test1, test3, test5, test7'
        }
        old_tags_data = set(['test1', 'test2', 'test3'])
        test_old_tags_data = set()
        tags_data = set(['test1', 'test3', 'test5', 'test7'])
        test_tags_data = set()
        question = Question.objects.get(id=1)
        tags = question.tag_set.all()
        self.assertEqual(len(tags), 3)
        for tag in tags:
            test_old_tags_data.add(tag.name)
        self.assertSetEqual(test_old_tags_data, old_tags_data)
        self.assertEqual(question.title, 'test')
        self.assertEqual(question.content, 'test content')
        response = self.client.post('/question/1/edit/', data)
        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(id=1)
        self.assertEqual(question.title, 'testing of editing title')
        self.assertEqual(question.content, 'new contents')
        tags = question.tag_set.all()
        self.assertEqual(len(tags), 4)
        for tag in tags:
            test_tags_data.add(tag.name)
        self.assertSetEqual(test_tags_data, tags_data)

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
            'answer_content': 'test answer 1',
        }
        self.client.post('/question/1/answer/', answer_data)
        self.client.get('/signout/')
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        answer_data = {
            'answer_content': 'test answer 2',
        }
        self.client.post('/question/1/answer/', answer_data)
        answer_data = {
            'answer_content': 'test answer 3',
        }
        self.client.post('/question/1/answer/', answer_data)
        self.client.get('/signout/')

    def test_get_not_login(self):
        response = self.client.get('/answer/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_get_not_exist(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/answer/5343/edit/')
        self.assertEqual(response.status_code, 404)

    def test_get_not_auth(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/answer/2/edit/')
        self.assertEqual(response.status_code, 403)

    def test_get_not_edit_action(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/answer/1/append/')
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/answer/1/edit/')
        self.assertEqual(response.status_code, 200)
        # TODO test more

    def test_post_not_login(self):
        data = {
            'answer_content': 'new answer',
        }
        response = self.client.post('/answer/1/edit/', data)
        self.assertEqual(response.status_code, 302)

    def test_post_not_exist(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'answer_content': 'new answer',
        }
        response = self.client.post('/answer/45/edit/', data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/answer/1023/append/', data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/answer/da1/comment/', data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/answer/1sdsa/vote/', data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/answer/3232/accept/', data)
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/answer/34asd1/delete/', data)
        self.assertEqual(response.status_code, 404)

    def test_post_not_auth_edit(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'answer_content': 'new answer',
        }
        response = self.client.post('/answer/1/edit/', data)
        self.assertEqual(response.status_code, 403)

    def test_post_not_auth_append(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'answer_append_content': 'appended answer',
        }
        response = self.client.post('/answer/1/append/', data)
        self.assertEqual(response.status_code, 403)

    def test_post_not_auth_accept(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.post('/answer/1/accept/')
        self.assertEqual(response.status_code, 403)

    def test_post_not_auth_delete(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.post('/answer/1/delete/')
        self.assertEqual(response.status_code, 403)

    def test_post_edit(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'answer_content': 'new answer',
        }
        answer = Question.objects.get(id=1).answer_set.first()
        self.assertEqual(answer.content, 'test answer 1')
        response = self.client.post('/answer/1/edit/', data)
        self.assertEqual(response.status_code, 302)
        answer = Question.objects.get(id=1).answer_set.first()
        self.assertEqual(answer.content, 'new answer')
        self.client.post('/signout/')
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'answer_content': 'new answer',
        }
        answer = Question.objects.get(id=1).answer_set.all()[1]
        self.assertEqual(answer.content, 'test answer 2')
        response = self.client.post('/answer/2/edit/', data)
        self.assertEqual(response.status_code, 302)
        answer = Question.objects.get(id=1).answer_set.all()[1]
        self.assertEqual(answer.content, 'new answer')

    def test_post_append(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'answer_append_content': 'appended answer',
        }
        append = Answer.objects.get(id=1).answerappend_set.first()
        self.assertIsNone(append)
        response = self.client.post('/answer/1/append/', data)
        self.assertEqual(response.status_code, 302)
        append = Answer.objects.get(id=1).answerappend_set.first()
        self.assertEqual(append.content, 'appended answer')
        self.client.post('/signout/')
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'answer_append_content': 'appended answer',
        }
        append = Answer.objects.get(id=2).answerappend_set.first()
        self.assertIsNone(append)
        response = self.client.post('/answer/2/append/', data)
        self.assertEqual(response.status_code, 302)
        append = Answer.objects.get(id=2).answerappend_set.first()
        self.assertEqual(append.content, 'appended answer')

    def test_post_comment(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'answer_comment_content': 'answer comment 1',
        }
        comment = Answer.objects.get(id=1).answercomment_set.first()
        self.assertIsNone(comment)
        response = self.client.post('/answer/1/comment/', data)
        self.assertEqual(response.status_code, 302)
        comment = Answer.objects.get(id=1).answercomment_set.first()
        self.assertEqual(comment.content, 'answer comment 1')
        self.assertEqual(comment.user.username, 'test1')
        data = {
            'answer_comment_content': 'answer comment 2',
        }
        response = self.client.post('/answer/2/comment/', data)
        self.assertEqual(response.status_code, 302)
        comment = Answer.objects.get(id=2).answercomment_set.first()
        self.assertEqual(comment.content, 'answer comment 2')
        self.assertEqual(comment.user.username, 'test1')
        self.client.post('/signout/')
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'answer_comment_content': 'answer comment 3',
        }
        response = self.client.post('/answer/1/comment/', data)
        self.assertEqual(response.status_code, 302)
        comment = Answer.objects.get(id=1).answercomment_set.all()[1]
        self.assertEqual(comment.content, 'answer comment 3')
        self.assertEqual(comment.user.username, 'test2')
        data = {
            'answer_comment_content': 'answer comment 4',
        }
        response = self.client.post('/answer/2/comment/', data)
        self.assertEqual(response.status_code, 302)
        comment = Answer.objects.get(id=2).answercomment_set.all()[1]
        self.assertEqual(comment.content, 'answer comment 4')
        self.assertEqual(comment.user.username, 'test2')

    def test_post_vote(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        vote = Answer.objects.get(id=1).answervote_set.first()
        self.assertIsNone(vote)
        response = self.client.post('/answer/1/upvote/')
        self.assertEqual(response.status_code, 302)
        votes = Answer.objects.get(id=1).answervote_set.all()
        vote = votes[0]
        self.assertEqual(len(votes), 1)
        self.assertTrue(vote.vote_type)
        response = self.client.post('/answer/1/upvote/')
        self.assertEqual(response.status_code, 302)
        votes = Answer.objects.get(id=1).answervote_set.all()
        self.assertEqual(len(votes), 1)
        response = self.client.post('/answer/1/downvote/')
        self.assertEqual(response.status_code, 302)
        vote = Answer.objects.get(id=1).answervote_set.first()
        self.assertIsNone(vote)
        self.client.get('/signout/')
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.post('/answer/1/upvote/')
        self.assertEqual(response.status_code, 302)
        vote = Answer.objects.get(id=1).answervote_set.first()
        self.assertIsNone(vote)

    def test_post_accept(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        answer = Answer.objects.get(id=1)
        question = Question.objects.get(id=1)
        response = self.client.post('/answer/1/accept/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(answer.accepted)
        self.assertFalse(question.solved)
        answer = Answer.objects.get(id=2)
        response = self.client.post('/answer/2/accept/')
        self.assertEqual(response.status_code, 302)
        answer = Answer.objects.get(id=2)
        question = Question.objects.get(id=1)
        self.assertTrue(answer.accepted)
        self.assertTrue(question.solved)
        response = self.client.post('/answer/3/accept/')
        self.assertEqual(response.status_code, 302)
        answer = Answer.objects.get(id=3)
        self.assertFalse(answer.accepted)

    def test_post_delete(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        question = Question.objects.get(id=1)
        self.assertFalse(question.solved)
        response = self.client.post('/answer/2/accept/')
        question = Question.objects.get(id=1)
        self.assertTrue(question.solved)
        response = self.client.post('/answer/1/delete/')
        self.assertEqual(response.status_code, 302)
        answer = Answer.objects.filter(id=1).first()
        self.assertIsNone(answer)
        self.client.get('/signout/')
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.post('/answer/2/delete/')
        self.assertEqual(response.status_code, 302)
        answer = Answer.objects.filter(id=2).first()
        question = Question.objects.get(id=1)
        self.assertIsNone(answer)
        self.assertFalse(question.solved)
