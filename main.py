#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


LOGIN = '<LOGIN>'
PASSWORD = '<PASSWORD>'


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'

URL_GITHUB = 'https://github.com/'
URL_GITHUB_LOGIN = 'https://github.com/login'
URL_GITHUB_EMAILS = 'https://github.com/settings/emails'


import sys
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s',
    handlers=[
        logging.FileHandler('log', encoding='utf8'),
        logging.StreamHandler(stream=sys.stdout),
    ],
)


def get_email():
    """Function for search email github user. If email not found, function return None."""

    logging.debug('Call get_email')
    logging.debug('Open profile page: %s', URL_GITHUB + LOGIN)

    # Search email on profile page
    browser.open(URL_GITHUB + LOGIN)

    match = browser.select('[itemprop="email"] > a')
    if match:
        logging.debug('Email found')
        return match[0].text
    else:
        logging.debug('Email on profile page is not found')
        logging.debug('Open settings/emails page: %s', URL_GITHUB_EMAILS)

        # Search email on settings page
        browser.open(URL_GITHUB_EMAILS)

        logging.debug('Search primary email')

        # Search primary email
        for li in browser.select('#settings-emails > li'):
            match = bool([label for label in li.select('span.label') if 'Primary' == label.text])
            if match:
                email = li.select('span.css-truncate-target')
                if email:
                    logging.debug('Email found')
                    return email[0].text

    logging.debug('Email not found')
    return None


if __name__ == '__main__':
    logging.debug('User agent: %s', USER_AGENT)

    from robobrowser import RoboBrowser
    browser = RoboBrowser(
        user_agent=USER_AGENT,
        parser='lxml'
    )
    logging.debug('Auth to github, login page: %s', URL_GITHUB_LOGIN)
    browser.open(URL_GITHUB_LOGIN)

    logging.debug('Fill login and password')
    signup_form = browser.get_form()
    signup_form['login'].value = LOGIN
    signup_form['password'].value = PASSWORD

    # Submit the form
    logging.debug('Submit the form')
    browser.submit_form(signup_form)

    email = get_email()
    print(email)
