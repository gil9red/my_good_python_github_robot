#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from config import *


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


def search_login_and_path(browser, url_pattern, find_users_dict):
    page = 1
    max_page = None

    while True:
        log.debug('Load search %s page: %s', page, url_pattern.format(page))
        browser.open(url_pattern.format(page))

        if 'You have triggered an abuse detection mechanism.' in browser.response.text:
            timeout = 15
            log.debug('"You have triggered an abuse detection mechanism. Please wait '
                      'a few minutes before you try again.", wait %s seconds.', timeout)
            time.sleep(timeout)
            continue

        # Init only on first page
        if max_page is None:
            max_page = int(browser.select('.pagination a')[-2].text)

        for item in browser.select('.code-list > .code-list-item'):
            title = item.select('.title a')[1]
            from urllib.parse import urljoin

            href = title['href']
            user = href.split('/')[1]
            url_file = urljoin(browser.url, href)
            code = ''.join(code.text.strip() for code in item.select('.file-box .blob-code'))
            print(user, url_file)
            print(code)

            for pattern in login_and_pass_patterns:
                for login, password in pattern.findall(code):
                    print(user, password)
                    find_users_dict[login, password] = (user, url_file)

                    # match = pattern.search(code)
                    # if match:
                    #     login, password = match.group(1), match.group(2)
                    #     print(user, password)
                    #     find_users.add((user, login, password, url_file))

            print()

        if page >= max_page:
            log.debug('Last search page')
            break

        page += 1
        # break


if __name__ == '__main__':
    log.debug('User agent: %s', USER_AGENT)

    from robobrowser import RoboBrowser
    browser = RoboBrowser(
        user_agent=USER_AGENT,
        parser='lxml'
    )

    auth_is_successful = check_auth(browser, LOGIN, PASSWORD)
    log.debug('Authorization successful' if auth_is_successful else 'Authorization is not successful')

    # if auth_is_successful:
    #     email = get_email(browser, LOGIN)
    #     log.debug('Email: %s', email)

    import re
    import time

    login_and_pass_patterns = [
        # re.compile(r'''auth\s*=\s*\(['"](.+?)['"],\s*['"](.+?)['"]\)\s*\)'''),
        # re.compile(r'''HTTPBasicAuth\s*\(['"](.+?)['"],\s*['"](.+?)['"]\)\s*\)'''),
        # re.compile(r'''HTTPDigestAuth\s*\(['"](.+?)['"],\s*['"](.+?)['"]\)\s*\)'''),
        re.compile(r'''HTTP\w+Auth\s*\(['"](.+?)['"],\s*['"](.+?)['"]\)\s*\)'''),

        re.compile(r'''auth\s*=\s*\w*?\s*\(['"](.+?)['"],\s*['"](.+?)['"]\)\s*\)'''),
    ]

#     text = '''
# # -*- coding:utf-8 -*-import requestsfrom requests.auth import AuthBasefrom requests.auth import HTTPBasicAuth# r = requests.get('https://api.github.com/user', auth=HTTPBasicAuth('user', 'pass'))# 直接使用r = requests.get('https://api.github.com/user', auth=('johnChnia', 'zhouqiang8520604'))
#     '''
#
#     text = ' '.join(row.strip() for row in text.split('\n'))
#     # print(text)
#
#     find_users = set()
#
#     for pattern in login_and_pass_patterns:
#         print(pattern.findall(text))
#         for i in pattern.findall(text):
#             find_users.add(i)
#
#     print(find_users)
#
#     quit()

    if auth_is_successful:
        find_users_dict = dict()

        URL_GITHUB_SEARCH_MATCH = 'https://github.com/search?p={}&q=requests+auth+github+filename%3A.py' \
                                  '&ref=searchresults&type=Code&utf8=%E2%9C%93'

        URL_GITHUB_SEARCH_RECENTLY_INDEXED = 'https://github.com/search?p={}&o=desc&q=requests+auth+github+filename' \
                                             '%3A.py&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93'

        URL_GITHUB_SEARCH_LEAST_RECENTLY_INDEXED = 'https://github.com/search?p={}&o=asc&q=requests+auth+github+' \
                                                   'filename%3A.py&ref=searchresults&s=indexed&type=Code&utf8=%E2%9C%93'

        search_login_and_path(browser, URL_GITHUB_SEARCH_MATCH, find_users_dict)
        search_login_and_path(browser, URL_GITHUB_SEARCH_RECENTLY_INDEXED, find_users_dict)
        search_login_and_path(browser, URL_GITHUB_SEARCH_LEAST_RECENTLY_INDEXED, find_users_dict)

    print('\n\n', '-' * 50, '\n\n')
    # print(find_users_dict)

    for i, ((login, password), (user, url_file)) in enumerate(find_users_dict.items(), 1):
        print('{}. "{}", {}/{}: {}'.format(i, user, login, password, url_file))
