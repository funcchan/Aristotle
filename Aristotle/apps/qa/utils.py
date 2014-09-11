#!/usr/bin/env python
#
# @name: utils.py
# @create: Sep. 4th, 2014
# @update: Sep. 10th, 2014
# @author: hitigon@gmail.com
import re
import time
import calendar
import random
import hashlib
import base64
from django.utils import timezone
from datetime import timedelta


def parse_listed_strs(strs, delim=None):
    # parse tags, uris
    if not strs:
        return set()
    result = set()
    for sub in re.split(delim or ';|,| |\n', strs):
        sub = sub.strip()
        if len(sub) > 0:
            result.add(sub)
    return result


def get_utc_timestamp():
    return calendar.timegm(time.gmtime())


def format_time_path(path):
    return time.strftime(path, time.gmtime())


def get_utc_time(seconds=0):
    return timezone.now() + timedelta(0, seconds)


def create_unique_code():
    s = hashlib.sha256(str(random.getrandbits(256))).digest()
    chars = random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])
    return base64.b64encode(s, chars).rstrip('==')
