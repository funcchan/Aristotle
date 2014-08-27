#!/usr/bin/env python
from django.http import HttpRequest
from django.test import TestCase
from django.core.urlresolvers import resolve

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

