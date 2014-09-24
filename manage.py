#!/usr/bin/env python
import logging
import os
import sys

FORMAT = '[%(levelname)s %(asctime)s] %(filename)s: %(message)s'
logging.basicConfig(level=logging.ERROR, format=FORMAT)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Aristotle.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
