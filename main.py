#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


LOGIN = '<LOGIN>'
PASSWORD = '<PASSWORD>'


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


def check_auth(browser, login, password):
    """Function return true if authorization in github by login and password is successful."""

    log.debug('Authorization to github, login page: %s', URL_GITHUB_LOGIN)
    browser.open(URL_GITHUB_LOGIN)

    log.debug('Fill login and password')
    signup_form = browser.get_form()
    signup_form['login'].value = login
    signup_form['password'].value = password

    # Submit the form
    log.debug('Submit the form')
    browser.submit_form(signup_form)

    # If not found error text on page
    return 'Incorrect username or password' not in browser.response.text


def get_email(browser, login):
    """Function for search email github user. If email not found, function return None."""

    log.debug('Call get_email')
    log.debug('Open profile page: %s', URL_GITHUB + login)

    # Search email on profile page
    browser.open(URL_GITHUB + login)

    match = browser.select('[itemprop="email"] > a')
    if match:
        log.debug('Email found')
        return match[0].text
    else:
        log.debug('Email on profile page is not found')
        log.debug('Open settings/emails page: %s', URL_GITHUB_EMAILS)

        # Search email on settings page
        browser.open(URL_GITHUB_EMAILS)

        log.debug('Search primary email')

        # Search primary email
        for li in browser.select('#settings-emails > li'):
            match = bool([label for label in li.select('span.label') if 'Primary' == label.text])
            if match:
                email = li.select('span.css-truncate-target')
                if email:
                    log.debug('Email found')
                    return email[0].text

    log.debug('Email not found')
    return None


if __name__ == '__main__':
    log.debug('User agent: %s', USER_AGENT)

    from robobrowser import RoboBrowser
    browser = RoboBrowser(
        user_agent=USER_AGENT,
        parser='lxml'
    )

    auth_is_successful = check_auth(browser, LOGIN, PASSWORD)
    log.debug('Authorization successful' if auth_is_successful else 'Authorization is not successful')

    if auth_is_successful:
        email = get_email(browser, LOGIN)
        log.debug('Email: %s', email)
