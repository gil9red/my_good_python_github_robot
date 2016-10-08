#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


LOGIN = '<LOGIN>'
PASSWORD = '<PASSWORD>'


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'

URL_GITHUB = 'https://github.com/'
URL_GITHUB_LOGIN = URL_GITHUB + 'login'
URL_GITHUB_EMAILS = URL_GITHUB + 'settings/emails'


if __name__ == '__main__':
    from robobrowser import RoboBrowser

    browser = RoboBrowser(
        user_agent=USER_AGENT,
        parser='lxml'
    )
    browser.open(URL_GITHUB_LOGIN)

    signup_form = browser.get_form()
    signup_form['login'].value = LOGIN
    signup_form['password'].value = PASSWORD

    # Submit the form
    browser.submit_form(signup_form)

    class NotFoundEmail(Exception):
        pass

    def get_email():
        # Search email on profile page
        browser.open(URL_GITHUB + LOGIN)
        match = browser.select('[itemprop="email"] > a')
        if match:
            return match[0].text
        else:
            # Search email on settings page
            browser.open(URL_GITHUB_EMAILS)

            # Search primary email
            for li in browser.select('#settings-emails > li'):
                match = bool([label for label in li.select('span.label') if 'Primary' == label.text])
                if match:
                    email = li.select('span.css-truncate-target')
                    if email:
                        print(email[0].text)
                    else:
                        raise NotFoundEmail()

    email = get_email()
    print(email)
