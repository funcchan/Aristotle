#!/usr/bin/env python

from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User
from Aristotle.apps.qa.models import Member


class MemberTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test', password='test', email='test@email.com')
        self.member = Member.objects.create(user=self.user)
        self.member.save()

    def test_init_member(self):
        member = self.member
        self.assertEqual(member.gender, 'Unknown')
        self.assertEqual(member.age, 0)
        self.assertEqual(member.occupation, '')
        self.assertEqual(member.education, '')
        self.assertEqual(member.address, '')
        self.assertEqual(member.phone, '')
        self.assertEqual(member.company, '')
        self.assertEqual(member.website, '')
        self.assertEqual(member.interests, '')
        self.assertEqual(member.bio, '')
        self.assertEqual(member.last_login_ip, '')
        # self.assertEqual(member.avatar, '')

    def test_duplicated_user(self):
        with self.assertRaises(IntegrityError):
            Member.objects.create(user=self.user)

    def test_update_member(self):
        member = self.member
        member.gender = 2
        member.age = 20
        member.occupation = 'Programmer'
        member.education = 'High school'
        member.address = '1234 Mission St. SF, CA 90000'
        member.phone = '1-510-100-1000'
        member.company = 'Google Inc.'
        member.website = 'http://google.com'
        member.interests = 'coding,cooking,runing'
        member.bio = 'About myself'
        member.last_login_ip = '127.0.0.1'
        # member.avatar = '/sss/xxx/ggg.png'
        member.save()
        self.assertEqual(member.gender, 2)
        self.assertEqual(member.age, 20)
        self.assertEqual(member.occupation, 'Programmer')
        self.assertEqual(member.education, 'High school')
        self.assertEqual(member.address, '1234 Mission St. SF, CA 90000')
        self.assertEqual(member.phone, '1-510-100-1000')
        self.assertEqual(member.company, 'Google Inc.')
        self.assertEqual(member.website, 'http://google.com')
        self.assertEqual(member.interests, 'coding,cooking,runing')
        self.assertEqual(member.bio, 'About myself')
        self.assertEqual(member.last_login_ip, '127.0.0.1')
        # self.assertEqual(member.avatar, '/sss/xxx/ggg.png')


class QuestionTest(TestCase):

    def setUp(self):
        pass
