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

import dynamodb
import logging
import telegram
from translation import Translation
from settings import CONFIG, STATUSES
import globalvars

logger = logging.getLogger()
logger.setLevel(CONFIG['LOG_LEVEL'])

def save_chat_status(chat_id, status):
    """
    Saves chat state
    
    :param chat_id: Telegram Chat ID
    :param status: state
    :return: True if stored, False otherwise
    """
    return dynamodb.save_chat_status(
        table=CONFIG['DYNAMO_TABLE'],
        chat_id=chat_id,
        status=status
    )

def make_language_keyboard():
    """
    Create language selection keyboard

    :return: A telegram keyboard
    """
    return telegram.make_keyboard(
        globalvars.lang.text('SUPPORTED_LANGUAGES'),
        2,
        '')

def represents_int(s):
    """
    Is it an integer

    :param s: String to be tested
    :return: True if interger, False otherwise
    """
    try:
        int(s)
        return True
    except ValueError:
        return False

def get_tos_link():
    """
    Returns Terms of Service link

    :return: A string containing TOS link
    """
    return dynamodb.get_info_link(
            CONFIG['INFO_DYNAMO_TABLE'],
            globalvars.lang.language,
            'termsofservice'
        ) 


def get_pp_link():
    """
    Returns Privacy Policy link

    :return: A string containing privacy policy link
    """
    return dynamodb.get_info_link(
            CONFIG['INFO_DYNAMO_TABLE'],
            globalvars.lang.language,
            'privacypolicy'
        )


def change_lang(new_lang):
    """
    Change langiage of the user and apply the required changes

    :param new_lang: New language to be stored
    """
    try:
        globalvars.lang = Translation(new_lang, CONFIG['LANGUAGE_FILE'])
    except Exception as exc:
        logger.error("Error in Language file!")
        return None
        
    globalvars.HOME_KEYBOARD = [
        [
            globalvars.lang.text('MENU_HOME_EXISTING_KEY'),
            globalvars.lang.text('MENU_HOME_NEW_KEY')
        ],
        [
            globalvars.lang.text('MENU_HOME_FAQ'),
            globalvars.lang.text('MENU_HOME_INSTRUCTION')
        ],
        [
            globalvars.lang.text('MENU_HOME_CHANGE_LANGUAGE'),
            globalvars.lang.text('MENU_HOME_PRIVACY_POLICY')
        ],
        [
            globalvars.lang.text('MENU_HOME_SUPPORT'),
            globalvars.lang.text('MENU_HOME_DELETE_ACCOUNT')
        ],
        [
            globalvars.lang.text('MENU_CHECK_STATUS'),
        ]
    ]

    globalvars.BACK_TO_HOME_KEYBOARD = [
        [globalvars.lang.text('MENU_BACK_HOME')]
    ]

    if new_lang in ['fa', 'ar']:
        globalvars.OPT_IN_KEYBOARD = [
            [
                globalvars.lang.text('MENU_PRIVACY_POLICY_DECLINE'),
                globalvars.lang.text('MENU_PRIVACY_POLICY_CONFIRM')
            ]
        ]
    else:
        globalvars.OPT_IN_KEYBOARD = [
            [
                globalvars.lang.text('MENU_PRIVACY_POLICY_CONFIRM'),
                globalvars.lang.text('MENU_PRIVACY_POLICY_DECLINE')
            ]
        ]

    globalvars.OPT_IN_DECLINED_KEYBOARD = [
        [
            globalvars.lang.text('MENU_BACK_PRIVACY_POLICY'),
            globalvars.lang.text('MENU_HOME_CHANGE_LANGUAGE')
        ]
    ]
