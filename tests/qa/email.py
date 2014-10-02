#!/usr/bin/env python
#
# @name:  email.py
# @create: 01 October 2014 (Wednesday)
# @update: 01 October 2014 (Wednesday)
# @author: Z. Huang
from django.core import mail
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from Aristotle.apps.qa.notification import EmailNotification


class VerficationTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@test.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)
        user = User.objects.get(id=1)
        self.email = EmailNotification(user)

    def test_email(self):
        mail.outbox = []
        self.email.send_verfication()
        self.assertEqual(len(mail.outbox), 1)
        subject = 'Please verify your account for website name'
        self.assertEqual(mail.outbox[0].subject, subject)


class ResetPasswordTest(TestCase):

    def setUp(self):
        self.client = Client()
        user_data = {'username': 'test',
                     'email': 'test@test.com',
                     'password': 'test',
                     'repassword': 'test'}
        self.client.post('/signup/', user_data)
        user = User.objects.get(id=1)
        self.email = EmailNotification(user)

    def test_email(self):
        mail.outbox = []
        self.email.send_reset_password()
        self.assertEqual(len(mail.outbox), 1)
        subject = 'Reset your password'
        self.assertEqual(mail.outbox[0].subject, subject)
