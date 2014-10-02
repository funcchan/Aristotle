#!/usr/bin/env python
#
# @name: views.py
# @create: Sep. 10th, 2014
# @update: 01 October 2014 (Wednesday)
# @author: Z. Huang
import logging
from django.core.mail import send_mail
from models import ResetPassword
from utils import create_unique_code

logger = logging.getLogger(__name__)


class EmailNotification(object):

    def __init__(self, user):
        self.user = user

    def send_verfication(self):
        """only for testing purposes
        """
        # TODO create email nofitication templates
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
            return True
        except Exception as e:
            logger.error(str(e))
            return False
        return False

    def send_reset_password(self):
        """only for testing purposes
        """
        subject = 'Reset your password'
        message = 'Please use the address\n'
        from_email = 'donotreply@something.com'
        to_email = self.user.email
        try:
            code = create_unique_code()
            message += 'http://127.0.0.1:8001/reset/%s' % code
            reset = ResetPassword.objects.filter(user=self.user)
            if reset:
                reset.delete()
            ResetPassword.objects.create(user=self.user, code=code).save()
            send_mail(subject, message, from_email, [to_email, ])
            return True
        except Exception as e:
            logger.error(str(e))
            return False
        return False
