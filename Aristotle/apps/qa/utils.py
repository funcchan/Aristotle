#!/usr/bin/env python
#
# @name: utils.py
# @create: Sep. 4th, 2014
# @update: Sep. 4th, 2014
# @author: hitigon@gmail.com
import re


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
