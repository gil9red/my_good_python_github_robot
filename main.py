#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import traceback

from config import *


class BotSeveralAuthFail(Exception):
    pass


class BotAuthFail(Exception):
    pass


# TODO: use logging


def send_email(to_email, subject, text, text_subtype='plain'):
    username = MY_EMAIL_LOGIN
    password = MY_EMAIL_PASSWORD

    smtp_server = "smtp.gmail.com"

    # email отправителя, т.е. наша почта
    sender = MY_EMAIL_LOGIN

    # Получатели копии письма
    to_cc_emails = [
        # sender,
    ]

    # typical values for text_subtype are plain, html, xml
    text_subtype = text_subtype

    from email.mime.text import MIMEText
    msg = MIMEText(text, text_subtype)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    msg['Cc'] = ', '.join(to_cc_emails)

    # # this invokes the secure SMTP protocol (port 465, uses SSL)
    from smtplib import SMTP_SSL as SMTP

    # use this for standard SMTP protocol   (port 25, no encryption)
    # from smtplib import SMTP

    with SMTP(smtp_server, 465) as smtp:
        smtp.set_debuglevel(EMAIL_DEBUG)
        smtp.login(username, password)
        smtp.send_message(msg)


def get_text_email(file_urls):
    parts = ['<ol>']

    for url in file_urls:
        url_parts = url.split('/')
        _, _, _, user, repo, *_ = url_parts
        file = url_parts[-1]

        parts.append('<li>')
        parts.append('<a href="{0}">{1}/{2} - {3}</a>'.format(url, user, repo, file))
        parts.append('</li>')

    parts.append('</ol>')
    text = ''.join(parts)
    return PATTERN_EMAIL.format(text)


def check_response(browser):
    # If "Too Many Requests"
    if browser.response.status_code == 429:
        raise BotSeveralAuthFail()

    # if 'There have been several failed attempts to sign in from this account or IP address. ' \
    #    'Please wait a while and try again later' in browser.response.text:
    #     raise BotSeveralAuthFail()

    if 'Rate limit' in browser.select('head > title')[0].text:
        raise BotSeveralAuthFail()


def check_auth(login, password, browser=None):
    """Function return true if authorization in github by login and password is successful."""

    browser.open(URL_GITHUB_LOGIN)
    check_response(browser)

    signup_form = browser.get_form()

    try:
        signup_form['login'].value = login
        signup_form['password'].value = password

        # Submit the form
        browser.submit_form(signup_form)

    except Exception as e:
        raise BotSeveralAuthFail(e)

    check_response(browser)

    # If not found error text on page
    return 'Incorrect username or password' not in browser.response.text


def get_email(browser=None):
    """Function for search email github user. If email not found, function return None."""

    # Get login using regular expressions
    # import re
    # match = re.search('Signed in as <strong class="css-truncate-target">(.+?)</strong>', browser.response.text)
    # print(match.group(1))

    login = browser.select('.dropdown-menu .dropdown-item')[3]['href']

    from urllib.parse import urljoin

    # Search email on profile page
    browser.open(urljoin(URL_GITHUB, login))

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
                    return email[0].text

    return None


if __name__ == '__main__':
    if PROXY:
        import os
        os.environ['http_proxy'] = PROXY

    from github import Github
    gh = Github(MY_GITHUB_LOGIN, MY_GITHUB_PASSWORD)

    search_query = 'requests auth github filename:.py language:python'

    # The Search API has a custom rate limit. For requests using Basic Authentication, OAuth, or client ID and
    # secret, you can make up to 30 requests per minute. For unauthenticated requests, the rate limit allows
    # you to make up to 10 requests per minute.
    #
    # Если авторизован, то каждые 2 секунды можно слать запрос, иначе каждые 6
    timeout = 2 if MY_GITHUB_LOGIN and MY_GITHUB_PASSWORD else 6

    # Немного добавить на всякий
    timeout += 0.5

    import time
    from base64 import b64decode as base64_to_text

    search_result = gh.search_code(search_query)
    total_count = search_result.totalCount
    page = 0

    import re
    login_and_pass_patterns = [
        re.compile(r'''HTTP\w+Auth\s*\(['"](.+?)['"],\s*['"](.+?)['"]\)\s*\)'''),
        re.compile(r'''auth\s*=\s*\w*?\s*\(['"](.+?)['"],\s*['"](.+?)['"]\)\s*\)'''),
    ]

    from robobrowser import RoboBrowser

    from collections import defaultdict
    login_password_by_file_urls = defaultdict(set)

    while total_count > 0:
        try:
            data = search_result.get_page(page)
            # print(data)
            for result in data:
                # get user from repo url
                name = result.html_url.split('/')[3]

                # Check code
                code = base64_to_text(result.content.strip().encode()).decode()
                for pattern in login_and_pass_patterns:
                    for login, password in pattern.findall(code):
                        login_password_by_file_urls[login, password].add(result.html_url)

        except Exception as e:
            if 'Only the first 1000 search results are available' in str(e):
                break

            print("ERROR: ", e, type(e), traceback.format_exc())
            print("Wait 60 secs")
            time.sleep(60)
            continue

        print('page: {}, total: {}, login/password: {}'.format(page, total_count, len(login_password_by_file_urls)))
        page += 1
        total_count -= len(data)

        # Timeout before next request
        time.sleep(timeout)

    # Removing popular unused pairs of login and password
    for auth in [('user', 'password'), ('user', 'user'), ('password', 'password'), ('admin', 'pass'), ('user', 'pass'),
                 ('user', 'pwd'), ('user', '*****'), ('name', 'password'), ('github_user', 'github_password'),
                 ('user', 'password2')]:
        try:
            login_password_by_file_urls.pop(auth)
        except KeyError:
            pass

    # Check login/password
    for (login, password), urls in login_password_by_file_urls.items():
        try:
            while True:
                browser = RoboBrowser(user_agent=USER_AGENT, parser='lxml')

                try:
                    # Check login and password
                    if not check_auth(login, password, browser):
                        raise BotAuthFail()

                    # Get email from page or settings page
                    email = get_email(browser)

                    print('Send email to', email)
                    text = get_text_email(urls)
                    send_email(email, SUBJECT_EMAIL, text, 'html')

                    # All ok, exit loop
                    break

                except BotSeveralAuthFail as e:
                    print(traceback.format_exc())

                    secs = 300
                    print('BotSeveralAuthFail, New attempt in {} seconds'.format(secs))

                    # New attempt in <secs> seconds
                    time.sleep(secs)

        # If login and password did not match
        except BotAuthFail as e:
            continue

        except Exception as e:
            print(browser.response.ok, browser.response.reason, browser.response.status_code)
            print("ERROR: ", e, traceback.format_exc())
            open('html.html', 'w', encoding='utf-8').write(browser.response.text)

        print()
