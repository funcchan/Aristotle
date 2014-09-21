#!/usr/bin/env python
#
# @name: views.py
# @create:
# @update: Sep. 20th, 2014
# @author: Z. Huang
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from Aristotle.apps.qa.models import Member


class SignInTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test', password='test', email='test@test.com')

    def test_signin(self):
        response = self.client.get('/signin/')
        self.assertEqual(response.status_code, 200)

    def test_error(self):
        response = self.client.post('/signin/',
                                    {'username': 'wrong', 'password': 'wrong'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session, {})

    def test_normal(self):
        response = self.client.post('/signin/',
                                    {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.client.session, {})


class SignUpTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_signup(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)

    def test_normal(self):
        data = {'username': 'test',
                'email': 'test@gmail.com',
                'password': 'test',
                'repassword': 'test'}
        response = self.client.post('/signup/', data)
        user = User.objects.get(username='test')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.email, 'test@gmail.com')

    def test_miss_fields(self):
        data = {'username': 'test',
                'password': 'test'}
        response = self.client.post('/signup/', data)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username='test')
        self.assertEqual(response.status_code, 302)

    def test_not_identical_passwords(self):
        data = {'username': 'test',
                'email': 'test@gmail.com',
                'password': 'test',
                'repassword': 'test '}
        response = self.client.post('/signup/', data)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(username='test')
        self.assertEqual(response.status_code, 302)


class SignOutTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test', password='test', email='test@test.com')
        self.client.login(username='test', password='test')

    def test_signout(self):
        self.assertNotEqual(self.client.session, {})
        old_session = self.client.session
        response = self.client.get('/signout/')
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.client.session, old_session)


class ProfileTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test', password='test', email='test@test.com')
        Member.objects.create(user=self.user).save()

    def test_profile(self):
        response = self.client.get('/profile/1/')
        self.assertEqual(response.status_code, 200)

    def test_not_exist(self):
        response = self.client.get('/profile/2/')
        self.assertEqual(response.status_code, 404)

    def test_logged(self):
        self.client.post('/signin/', {'username': 'test', 'password': 'test'})
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_not_logged(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 403)


class EditProfileTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='test1', password='test', email='test1@test.com')
        Member.objects.create(user=self.user1).save()
        self.user2 = User.objects.create_user(
            username='test2', password='test', email='test2@test.com')
        Member.objects.create(user=self.user2).save()

    def test_get_not_logged_profile(self):
        response = self.client.get('/profile/edit/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_get_profile(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/edit/')
        self.assertEqual(response.status_code, 200)

    def test_get_id_profile(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_get_unauth_id_profile(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.get('/profile/1/edit/')
        self.assertEqual(response.status_code, 403)

    def test_get_not_exist_id_profile(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/3/edit/')
        self.assertEqual(response.status_code, 404)
