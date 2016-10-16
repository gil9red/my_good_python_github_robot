#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


# Search by code without auth not working
MY_GITHUB_LOGIN = '<LOGIN>'
MY_GITHUB_PASSWORD = '<PASSWORD>'

# http://user:password@proxy_host:proxy_port
PROXY = None

# Our email
MY_EMAIL_LOGIN = '<EMAIL_LOGIN>'
MY_EMAIL_PASSWORD = '<EMAIL_PASSWORD>'
EMAIL_DEBUG = False

SUBJECT_EMAIL = 'I found your username and password from github'
PATTERN_EMAIL = """
Hi, I'm <b>Good Robot</b>!<br>
I found your login and password on github here:
{}

<hr>
<a href="https://github.com/gil9red/my_good_python_github_robot">My project here</a>

"""

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'

URL_GITHUB = 'https://github.com/'
URL_GITHUB_LOGIN = 'https://github.com/login'
URL_GITHUB_EMAILS = 'https://github.com/settings/emails'


def get_logger(name, file='log.txt', encoding='utf8'):
    import logging
    import sys

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s')

    fh = logging.FileHandler(file, encoding=encoding)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)

    return log


log = get_logger('my_good_python_github_robot')
