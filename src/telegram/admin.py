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
import api
import telegram
from errors import ValidationError
from urllib.parse import urlparse
from settings import CONFIG, STATUSES
from helpers import (
    make_language_keyboard,
    save_chat_status,
    get_tos_link,
    get_pp_link,
    change_lang)
import globalvars

def is_url(link):
    """
    Checks the validity of a URL

    :param link: A string containing the link to be tested
    :return: Link is a valid URL or not - Boolean
    """
    if link is None or len(link) == 0:
        return False
    urlp = urlparse(link)
    if urlp.scheme == '' or urlp.netloc == '':
        return False
    return True

def store_tos_link(link):
    """
    Stores Terms of Service link

    :param link: A string containing the link to be stored
    :return: True if link is stored False otherwise
    """
    if not is_url(link):
        return False
    return dynamodb.save_info_link(
        CONFIG['INFO_DYNAMO_TABLE'],
        link,
        globalvars.lang.language,
        'termsofservice'
    ) 

def store_pp_link(link):
    """
    Stores Privacy Policy link

    :param link: A string containing the link to be stored
    :return: True if link is stored False otherwise
    """
    if not is_url(link):
        return False
    return dynamodb.save_info_link(
        CONFIG['INFO_DYNAMO_TABLE'],
        link,
        globalvars.lang.language,
        'privacypolicy'
    )

def make_admin_keyboard():
    """
    Creates the admin keyboard

    :return: Telegram Keyboard containing admin commands
    """

    return telegram.make_keyboard(
        [
            globalvars.lang.text('MENU_ADMIN_BAN_USER'),
            globalvars.lang.text('MENU_ADMIN_TERMS_OF_SERVICE'),
            globalvars.lang.text('MENU_ADMIN_PRIVACY_POLICY'),
            globalvars.lang.text('MENU_ADMIN_ENROLLED_USERS'),
            globalvars.lang.text('MENU_ADMIN_BANNED_USERS'),
            globalvars.lang.text('MENU_ADMIN_BLOCKED_KEYS'),
            globalvars.lang.text('MENU_HOME_CHANGE_LANGUAGE'),
            globalvars.lang.text('MENU_ADMIN_EXIT')
        ],
        3,
        ''
    )        

def admin_menu(token, tmsg, chat_status):
    """
    Handles admin only menu

    :param token: Telegram Bot Token
    :param tmsg: Telegram message from user
    :param chat_status: Representing the state of the chat with the user
    
    :return: False in case user should not see admin menu
    """    
    if tmsg.user_uid not in CONFIG['ADMIN']:
        save_chat_status(tmsg.chat_id, STATUSES['HOME'])        
        return False

    admin_keyboard = make_admin_keyboard()

    if chat_status < STATUSES['ADMIN_SECTION_HOME']:
        telegram.send_keyboard(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_ADMIN_HOME'),
            admin_keyboard)
        save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SECTION_HOME'])
    elif chat_status == STATUSES['ADMIN_SECTION_HOME']:
        if (tmsg.body == globalvars.lang.text('MENU_ADMIN_EXIT')):
            save_chat_status(tmsg.chat_id, STATUSES['HOME'])
            return False
        elif (tmsg.body == globalvars.lang.text('MENU_ADMIN_BAN_USER')):
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ENTER_USER_TO_BAN'),
                '')
            save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SECTION_BAN_USER'])
        elif (tmsg.body == globalvars.lang.text('MENU_ADMIN_TERMS_OF_SERVICE')):
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_CURRENT_LINK').format(get_tos_link()))
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ENTER_TERMS_OF_SERVICE'))
            save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SECTION_TERMS_OF_SERVICE'])
        elif (tmsg.body == globalvars.lang.text('MENU_ADMIN_PRIVACY_POLICY')):
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_CURRENT_LINK').format(get_pp_link()))
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ENTER_PRIVACY_POLICY'))
            save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SECTION_PRIVACY_POLICY'])
        elif (tmsg.body == globalvars.lang.text('MENU_ADMIN_ENROLLED_USERS')):
            try:
                telegram.send_csv(token, tmsg.chat_id, api.get_enrolled_users(), 'enrolled_users.csv')
            except ValidationError:
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_ERROR'),
                    admin_keyboard)
                return True
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ADMIN_HOME'),
                admin_keyboard)
        elif (tmsg.body == globalvars.lang.text('MENU_ADMIN_BANNED_USERS')):
            try:
                telegram.send_csv(token, tmsg.chat_id, api.get_banned_users(), 'banned_users.csv')
            except ValidationError:
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_ERROR'),
                    admin_keyboard)
                return True
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ADMIN_HOME'),
                admin_keyboard)
        elif (tmsg.body == globalvars.lang.text('MENU_ADMIN_BLOCKED_KEYS')):
            try:
                telegram.send_csv(token, tmsg.chat_id, api.get_enrolled_users(blocked=True), 'blocked_keys.csv')
            except ValidationError:
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_ERROR'),
                    admin_keyboard)
                return True
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ADMIN_HOME'),
                admin_keyboard)
        elif (tmsg.body == globalvars.lang.text('MENU_HOME_CHANGE_LANGUAGE')):
            keyboard = make_language_keyboard()
            telegram.send_keyboard(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_SELECT_LANGUAGE'),
                keyboard)
            save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SET_LANGUAGE'])
        else:
            telegram.send_keyboard(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ADMIN_HOME'),
                admin_keyboard
            )
    elif chat_status == STATUSES['ADMIN_SECTION_BAN_USER']:
        ret = None
        try:
            ret = api.ban_user(tmsg.body)
        except Exception as exc:
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ERROR'),
                admin_keyboard)
            return True
        if ret is None or ret == {}:
            message = globalvars.lang.text('MSG_BAN_ERROR')
        else:
            message = globalvars.lang.text('MSG_BAN_SUCCESS')
        telegram.send_message(
            token,
            tmsg.chat_id,
            message
        )
        telegram.send_keyboard(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_ADMIN_HOME'),
            admin_keyboard
        )            
        save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SECTION_HOME'])    
    elif chat_status == STATUSES['ADMIN_SET_LANGUAGE']:
        if (tmsg.body is None or
                tmsg.body not in globalvars.lang.text(
                    'SUPPORTED_LANGUAGES')):
            message = globalvars.lang.text('MSG_LANGUAGE_CHANGE_ERROR')
        else:
            new_lang = CONFIG['SUPPORTED_LANGUAGES'][globalvars.lang.text(
                'SUPPORTED_LANGUAGES').index(tmsg.body)]
            dynamodb.save_user_lang(
                table=CONFIG["DYNAMO_TABLE"],
                chat_id=tmsg.chat_id,
                language=new_lang)
            change_lang(new_lang)
            admin_keyboard = make_admin_keyboard()
            message = globalvars.lang.text('MSG_LANGUAGE_CHANGED').format(tmsg.body)
            
        telegram.send_message(
                token,
                tmsg.chat_id,
                message)
        telegram.send_keyboard(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_ADMIN_HOME'),
                admin_keyboard)
        save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SECTION_HOME'])
    elif chat_status == STATUSES['ADMIN_SECTION_TERMS_OF_SERVICE']:
        if(store_tos_link(tmsg.body)):
            message = globalvars.lang.text('MSG_LINK_SAVED')            
        else:
            message = globalvars.lang.text('MSG_LINK_ERROR')
        save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SECTION_HOME'])
        telegram.send_message(
            token,
            tmsg.chat_id,
            message,
        )
        telegram.send_keyboard(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_ADMIN_HOME'),
            admin_keyboard
        )
        return True
    elif chat_status == STATUSES['ADMIN_SECTION_PRIVACY_POLICY']:
        if(store_pp_link(tmsg.body)):
            message = globalvars.lang.text('MSG_LINK_SAVED')            
        else:
            message = globalvars.lang.text('MSG_LINK_ERROR')
        save_chat_status(tmsg.chat_id, STATUSES['ADMIN_SECTION_HOME'])
        telegram.send_message(
            token,
            tmsg.chat_id,
            message,
        )
        telegram.send_keyboard(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_ADMIN_HOME'),
            admin_keyboard
        )
        return True
    else:
        save_chat_status(tmsg.chat_id, STATUSES['HOME'])
        return False

    return True
 