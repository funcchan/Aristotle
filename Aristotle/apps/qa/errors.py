#!/usr/bin/env python
#
# @name: errors.py
# @create: Aug. 28th, 2014
# @update: Aug. 28th, 2014
# @author: hitigon@gmail.com


class InvalidFieldError(Exception):

    def __init__(self, message=None, messages=None):
        Exception.__init__(self, message)
        self.messages = messages

    def __str__(self):
        pass
