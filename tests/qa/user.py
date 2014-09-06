#!/usr/bin/env python

from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User


class SignInTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test', password='test', email='test@test.com')

    def test_get(self):
        response = self.client.get('/signin/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/signin/',
                                    {'username': 'wrong', 'password': 'wrong'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session, {})

        response = self.client.post('/signin/',
                                    {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.client.session, {})
