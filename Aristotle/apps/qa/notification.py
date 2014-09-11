#!/usr/bin/env python
#
# @name: views.py
# @create: Sep. 10th, 2014
# @update: Sep. 10th, 2014
# @author: Z. Huang
from django.core.mail import send_mail, BadHeaderError
from utils import create_unique_code


class EmailNotification(object):

    def __init__(self, user):
        self.user = user

    def send_verfication(self):
        """only for testing purposes
        """
        subject = 'Please verify your account for website name'
        message = 'Thank you for signin up for website name!\n'
        message += 'To verify your account, please use the address\n'
        from_email = 'donotreply@something.com'
        to_email = self.user.email
        try:
            code = create_unique_code()
            self.user.activation.code = code
            self.user.activation.save()
            message += 'http://127.0.0.1:8001/activate/%s' % code
            send_mail(subject, message, from_email, [to_email, ])
        except BadHeaderError:
            # log the debug information
            return
        except Exception:
            # log
            return

    def send_reset_password(self):
        pass
