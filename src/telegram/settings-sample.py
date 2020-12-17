# coding=UTF-8
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

import logging

CONFIG = {
    'LOG_LEVEL': logging.INFO,
    'VERSION': '0.1.0',
    'BOT_ADMIN': 'OutlineAdmin',
    'SUPPORT_BOT': '',
    'ADMIN': $ADMIN_LIST,

    'DYNAMO_TABLE': '$AWS_DYNAMO_TABLE',
    'INFO_DYNAMO_TABLE': '$AWS_INFO_DYNAMO_TABLE',
    'API_KEY': '$API_KEY',
    'API_URL': '$API_URL',

    'TELEGRAM_START_COMMAND': 'start',
    'TELEGRAM_ADMIN_COMMAND': 'admin',
    'LANGUAGE_FILE': 'lang.json',
    'ITEMS_PER_ROW': 3,
    'MAX_ITEMS_PER_ROW': 4,
    'MSG_TIMEOUT': 33,
    'OUTLINE_AWS_URL': 'https://s3.amazonaws.com/outline-vpn/invite.html#{}',
    'OUTLINE_GUIDE_PHOTO_FILE': 'Pask-Outline-guideline.png',
    'OUTLINE_DELETE_PHOTO_FILE': 'Delete_previous_outline.png',
    'SUPPORTED_LANGUAGES': ['en', 'fa']
}

STATUSES = {
    'START': 0,
    'HOME': 1,
    'SET_LANGUAGE': 2,
    'FIRST_CAPTCHA': 3,
    'OPT_IN': 4,
    'OPT_IN_DECLINED': 5,
    'GET_EXISTING_KEY': 6,
    'GET_NEW_KEY': 7,
    'ASK_ISSUE': 8,
    'DELETE_ACCOUNT_REASON': 9,
    'DELETE_ACCOUNT_CONFIRM': 10,

    'ADMIN_SECTION_HOME': 1000,
    'ADMIN_SECTION_BAN_USER': 1001,
    'ADMIN_SECTION_TERMS_OF_SERVICE': 1002,
    'ADMIN_SECTION_PRIVACY_POLICY': 1004,
    'ADMIN_SET_LANGUAGE': 1006
}
