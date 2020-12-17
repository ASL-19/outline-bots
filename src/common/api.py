# Copyright 2020 ASL19 Organization
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import requests
from settings import CONFIG

logger = logging.getLogger()
USER_AGENT = 'Outline Telegram Bot'
AUTHORIZATION_HEADER = 'Token {}'


def get_enrolled_users(blocked=False):
    """
    Get a list of enrolled users from server

    :param blocked: boolean to indicate list of blocked users or all users
    :return: List of enrolled users as CSV
    """
    logger.info("getting enrolled users list from api server")
    url = '{}/distribution/listoutlineusers?format=csv'.format(CONFIG['API_URL'])
    if blocked:
        url += '&blocked=True'

    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    
    try:
        req = requests.get(url, headers=headers)
    except Exception as error:
        logger.error('get_enrolled_users error: {}'.format(error))
        raise error
    if req.status_code == requests.codes['ok']:
        return req.text
    else:
        logger.error(
            'API call error during get_enrolled_users. status: %s',
            str(req.status_code))
        req.raise_for_status()


def get_banned_users():
    """
    Get a list of enrolled users from server

    :return: List of enrolled users as CSV
    """
    logger.info("getting enrolled users list from api server")
    url = '{}/distribution/users?format=csv'.format(CONFIG['API_URL'])
    url += '&banned=True'

    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    
    try:
        req = requests.get(url, headers=headers)
    except Exception as error:
        logger.error('get_enrolled_users error: {}'.format(error))
        raise error
    if req.status_code == requests.codes['ok']:
        return req.text
    else:
        logger.error(
            'API call error during get_enrolled_users. status: %s',
            str(req.status_code))
        req.raise_for_status()


def ban_user(username):
    """
    Ban user on the server

    :param username: Telegram username
    :return: User's json object or None in case of success and raise error otherwise
    """
    logger.info("banning user from api server: {}".format(username))
    url = '{}/distribution/user'.format(CONFIG['API_URL'])
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    data = {
        'username': str(username),
        'banned': True
    }
    try:
        req = requests.patch(url, json=data, headers=headers)
    except Exception as error:
        logger.error('ban_user error: {}'.format(error))
        raise error
    if req.status_code == requests.codes['ok']:
        json_data = json.loads(req.text)
        return json_data
    elif req.status_code == requests.codes['not_found']:
        logger.error('User not found')
        return {}
    else:
        logger.error(
            'API call error during ban_user. status: %s',
            str(req.status_code))
        req.raise_for_status()


def get_user(user_id):
    """
    Getting user information from server

    :param user_id: Telegram User ID
    :return: User's json object or None in case of success and raise error otherwise
    """
    logger.info("getting user info from api server: {}".format(user_id))
    url = '{}/distribution/user/{}'.format(CONFIG['API_URL'], str(user_id))
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    
    try:
        req = requests.get(url, headers=headers)
    except Exception as error:
        logger.error('get_user error: {}'.format(error))
        raise error
    if req.status_code == requests.codes['ok']:
        json_data = json.loads(req.text)
        return json_data
    elif req.status_code == requests.codes['not_found']:
        logger.error('User not found')
        return {}
    else:
        logger.error(
            'API call error during get_user. status: %s',
            str(req.status_code))
        req.raise_for_status()


def create_user(user_id, channel='TG'):
    """
    Check whether the telegram user has a Outline account

    :param user_id: Telegram User ID
    :param channel: What platform user is using to get a key, default Telegram
    :return: User's json object in case of success and None otherwise
    """
    logger.info("Creating new user: {}".format(user_id))
    url = '{}/distribution/user'.format(CONFIG['API_URL'])
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    data = {
        'username': str(user_id),
        'channel': channel
    }

    try:
        req = requests.put(url, json=data, headers=headers)
    except Exception as error:
        logger.error('create_user error: {}'.format(error))
        raise error
    if req.status_code == requests.codes['ok']:
        json_data = json.loads(req.text)
        return json_data
    elif req.status_code == requests.codes['bad_request']:
        logger.error('Bad request, check the submitted data')
        return None
    elif req.status_code == requests.codes['conflict']:
        logger.error(
            'Bad request, Username already exists: {}'.format(user_id))
        return None
    else:
        logger.error(
            'API call error during create_user. status: %s',
            str(req.status_code))
        req.raise_for_status()


def get_outline_server_info(server_id):
    """
    Retrieve outline server info from the api server

    :param user_id: VPN Server ID
    :return: User's json object in case of success and None otherwise
    """
    logger.info("Get outline server info {}".format(str(server_id)))
    url = '{}/server/outlineserver/{}'.format(CONFIG['API_URL'], server_id)
    print(url)
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    try:
        req = requests.get(url, headers=headers)
    except Exception as error:
        logger.error('get_outline_server_info error: {}'.format(error))
        raise error

    if req.status_code == requests.codes['ok']:
        json_data = json.loads(req.text)
        return json_data
    elif req.status_code == requests.codes['bad_request']:
        logger.error('Bad request, check the submitted data')
        return None
    else:
        logger.error(
            'API call error during get_outline_server_info. status: %s',
            str(req.status_code))
        req.raise_for_status()


def get_outline_user(user_id):
    """
    Check whether the telegram user has a Outline account

    :param user_id: Telegram User ID
    :return: User's json object in case of success and None otherwise
    """
    logger.info("Get/update outline user info {}".format(user_id))
    url = '{}/distribution/outline/{}'.format(CONFIG['API_URL'], user_id)
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    try:
        req = requests.get(url, headers=headers)
    except Exception as error:
        logger.error('get_outline_user error: {}'.format(error))
        raise error
    if req.status_code == requests.codes['ok']:
        json_data = json.loads(req.text)
        return json_data
    elif req.status_code == requests.codes['bad_request']:
        logger.error('Bad request, check the submitted data')
        return None
    else:
        logger.error(
            'API call error during get_outline_user. status: %s',
            str(req.status_code))
        req.raise_for_status()


def get_new_key(user_id, user_issue=None):
    """
    Get a new key for the user

    :param user_id: Telegram User ID
    :param user_issue: Issue ID
    :return: User's json object in case of success and None otherwise
    """
    logger.info("Get a new key for {}".format(user_id))
    url = '{}/distribution/outline'.format(CONFIG['API_URL'])
    print(url)
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    data = {
        'user': str(user_id)
    }
    if user_issue:
        data['user_issue'] = int(user_issue)

    try:
        req = requests.put(url, json=data, headers=headers)
    except Exception as error:
        logger.error('get_new_key error: {}'.format(error))
        raise error

    if req.status_code == requests.codes['ok']:
        json_data = json.loads(req.text)
        return json_data['outline_key']
    elif req.status_code == requests.codes['bad_request']:
        logger.error('Bad request, check the submitted data')
        return None
    else:
        logger.error(
            'API call error during get_new_key. status: %s',
            str(req.status_code))
        req.raise_for_status()


def get_outline_sever_id(user_id):
    """
    Check whether the telegram user has a Outline account

    :param user_id: Telegram User ID
    :return: User's json object in case of success and None otherwise
    """
    logger.info("Get outline server id for user: {}".format(user_id))
    user = get_outline_user(user_id)
    if user is not None:
        return user['server']


def get_key(user_id, user_issue=None):
    """
    Check whether the telegram user has a Outline account

    :param user_id: Telegram User ID
    :param user_issue: Issue ID
    :return: User's json object in case of success and None otherwise
    """
    logger.info("Get new Outline key for user: {}".format(user_id))
    user = get_outline_user(user_id, user_issue)
    if user is not None:
        return user['outline_key']


def delete_user(user_id):
    """
    Delete the user's Outline account

    :param user_id: Telegram User ID
    :return: True if successful and False in case of any error
    """
    logger.info("Deleting user's profile: {}".format(user_id))
    url = '{}/distribution/user'.format(CONFIG['API_URL'])
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])
    }
    data = {
        'username': str(user_id)
    }

    try:
        req = requests.delete(url, json=data, headers=headers)
    except Exception as error:
        logger.error('delete_user error: {}'.format(error))
        raise error
    if req.status_code == requests.codes['no_content']:
        return True
    elif req.status_code == requests.codes['not_found']:
        logger.error('User not found')
        return False
    else:
        logger.error(
            'API call error during user_exits. status: %s',
            str(req.status_code))
        req.raise_for_status()


def get_issues(lang):
    """
    Get the list of issues from landing page server

    :param lang: user's current language to filter the issues
    :return: Dictionary of issues' id and description
    """
    logger.info("getting the list of issues from the api server.")
    url = '{}/distribution/issues'.format(CONFIG['API_URL'])
    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': AUTHORIZATION_HEADER.format(CONFIG['API_KEY'])}
    try:
        req = requests.get(url, headers=headers)
    except Exception as error:
        logger.error('get_user error: {}'.format(error))
        raise error

    lang_pattern = '_{}'.format(lang)
    issues = {}
    if req.status_code == requests.codes['ok']:
        json_data = json.loads(req.text)
        if 'results' in json_data:
            for result in json_data['results']:
                for key, value in result.items():
                    if str(key).endswith(lang_pattern):
                        issues[result['id']] = str(value)
                if result['id'] not in issues:
                    issues[result['id']] = result['description_en']
        return issues
    elif req.status_code == requests.codes['not_found']:
        logger.error('List of Issues not found')
        return {}
    else:
        logger.error(
            'API call error during get_issues. status: %s',
            str(req.status_code))
        req.raise_for_status()


def users(banned=False):
    """
    Return the list of all users or banned users

    :param banned: True to get banned users, False for all users=
    :retrun: A csv file including users' data
    """
    logger.info("getting all users from api server")
    if banned:
        url = '{}/users?banned=True&format=csv'.format(CONFIG['API_URL'])
    else:
        url = '{}/users?format=csv'.format(CONFIG['API_URL'])

    headers = {
        'User-Agent': USER_AGENT,
        'Authorization': API_PREFIX.format(CONFIG['API_KEY'])}
    try:
        req = requests.get(url, headers=headers)
    except Exception as error:
        logger.error('all_users error: {}'.format(error))
        raise

    if req.status_code == requests.codes['ok']:
        return req.text
    elif req.status_code == requests.codes['not_found']:
        logger.error('Users not found')
        return {}
    else:
        logger.error(
            'API call error during all_users. status: %s',
            str(req.status_code))
        req.raise_for_status()
