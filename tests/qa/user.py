#!/usr/bin/env python
#
# @name: views.py
# @create:
# @update: Sep. 25th, 2014
# @author: Z. Huang
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
        data = {'username': 'test',
                'email': 'test@gmail.com',
                'password': 'test',
                'repassword': 'test'}
        self.client.post('/signup/', data)
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
        data = {'username': 'test',
                'email': 'test@gmail.com',
                'password': 'test',
                'repassword': 'test'}
        self.client.post('/signup/', data)

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

    def test_get_not_login(self):
        response = self.client.get('/profile/edit/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile/1/edit/')
        self.assertEqual(response.status_code, 302)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/edit/')
        self.assertEqual(response.status_code, 200)

    def test_get_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/1/edit/')
        self.assertEqual(response.status_code, 200)

    def test_get_not_auth_id(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.get('/profile/1/edit/')
        self.assertEqual(response.status_code, 403)

    def test_get_not_exist_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/3/edit/')
        self.assertEqual(response.status_code, 404)

    def test_post_not_login(self):
        response = self.client.post(
            '/profile/edit/', {'first_name': 'test_user'})
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            '/profile/1/edit/', {'first_name': 'test_user'})
        self.assertEqual(response.status_code, 302)

    def test_post_not_auth_id(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.post(
            '/profile/1/edit/', {'first_name': 'test_user'})
        self.assertEqual(response.status_code, 403)
        user = User.objects.get(username='test1')
        self.assertEqual('', user.first_name)

    def test_post_not_exist_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.post(
            '/profile/3/edit/', {'first_name': 'test_user'})
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'first_name': 'test1',
            'last_name': 'test2',
            'age': '25',
            'gender': 'Male',
        }
        user = User.objects.get(username='test1')
        self.assertEqual('', user.first_name)
        self.assertEqual('', user.last_name)
        self.assertEqual(0, user.member.age)
        self.assertEqual('Unknown', user.member.gender)
        response = self.client.post(
            '/profile/edit/', data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='test1')
        self.assertEqual('test1', user.first_name)
        self.assertEqual('test2', user.last_name)
        self.assertEqual(25, user.member.age)
        self.assertEqual('Male', user.member.gender)

    def test_post_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'first_name': 'test2',
            'last_name': 'test1',
            'age': '30',
            'gender': 'Female',
        }
        user = User.objects.get(username='test1')
        self.assertEqual('', user.first_name)
        self.assertEqual('', user.last_name)
        self.assertEqual(0, user.member.age)
        self.assertEqual('Unknown', user.member.gender)
        response = self.client.post(
            '/profile/1/edit/', data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='test1')
        self.assertEqual('test2', user.first_name)
        self.assertEqual('test1', user.last_name)
        self.assertEqual(30, user.member.age)
        self.assertEqual('Female', user.member.gender)


class EditAccountTest(TestCase):

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

    def test_get(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/account/')
        self.assertEqual(response.status_code, 200)

    def test_get_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/1/account/')
        self.assertEqual(response.status_code, 200)

    def test_get_not_login(self):
        response = self.client.get('/profile/account/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile/1/account/')
        self.assertEqual(response.status_code, 302)

    def test_get_not_exist_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/3/account/')
        self.assertEqual(response.status_code, 404)

    def test_get_not_auth_id(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.get('/profile/1/account/')
        self.assertEqual(response.status_code, 403)

    def test_post_not_login(self):
        response = self.client.post(
            '/profile/account/', {'password': 'test'})
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            '/profile/1/account/', {'username': 'test1'})
        self.assertEqual(response.status_code, 302)

    def test_post_not_exist_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.post(
            '/profile/3/account/', {'username': 'test3'})
        self.assertEqual(response.status_code, 404)

    def test_post_not_auth_id(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.post(
            '/profile/1/account/', {'username': 'test2'})
        self.assertEqual(response.status_code, 403)

    def test_post_not_correct_password(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'password': 'test1',
            'username': 'test1',
            'email': 'test3@test.com',
            'newpassword': 'test2',
            'repassword': 'test2'
        }
        user = User.objects.get(username='test1')
        self.assertEqual('test1@test.com', user.email)
        response = self.client.post(
            '/profile/account/', data)
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='test1')
        self.assertNotEqual('test3@test.com', user.email)

    def test_post(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        data = {
            'password': 'test',
            'username': 'test1',
            'email': 'test@test.com',
            'newpassword': 'test1',
            'repassword': 'test1'
        }
        old_session = self.client.session
        user = User.objects.get(username='test1')
        self.assertEqual('test1@test.com', user.email)
        response = self.client.post(
            '/profile/account/', data)
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.client.session, old_session)
        user = User.objects.get(username='test1')
        self.assertEqual('test@test.com', user.email)

    def test_post_id(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        data = {
            'password': 'test',
            'username': 'test2',
            'email': 'test5@test.com',
            'newpassword': 'test2',
            'repassword': 'test2'
        }
        old_session = self.client.session
        user = User.objects.get(username='test2')
        self.assertEqual('test2@test.com', user.email)
        response = self.client.post(
            '/profile/2/account/', data)
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.client.session, old_session)
        user = User.objects.get(username='test2')
        self.assertEqual('test5@test.com', user.email)


class EditAvatarView(TestCase):

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

    def test_get_not_login(self):
        response = self.client.get('/profile/avatar/')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile/1/avatar/')
        self.assertEqual(response.status_code, 302)

    def test_get_not_exist_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/3/avatar/')
        self.assertEqual(response.status_code, 404)

    def test_get_not_auth_id(self):
        self.client.post('/signin/', {'username': 'test2', 'password': 'test'})
        response = self.client.get('/profile/1/avatar/')
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/avatar/')
        self.assertEqual(response.status_code, 200)

    def test_get_id(self):
        self.client.post('/signin/', {'username': 'test1', 'password': 'test'})
        response = self.client.get('/profile/1/avatar/')
        self.assertEqual(response.status_code, 200)
