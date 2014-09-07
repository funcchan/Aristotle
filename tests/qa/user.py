#!/usr/bin/env python

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


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
                                    {'username': 'wrong', 'password': 'test'})
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
