# -*- coding: utf-8 -*-
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
import time
import base64
from tmsg import TelegramMessage
import telegram
from errors import ValidationError
import dynamodb
from captcha import get_choice, check_captcha
import api
from admin import admin_menu
from helpers import (
    save_chat_status,
    make_language_keyboard,
    represents_int,
    change_lang,
    get_pp_link,
    get_tos_link)
import globalvars

from settings import CONFIG, STATUSES
import urllib.parse

logger = logging.getLogger()
logger.setLevel(CONFIG['LOG_LEVEL'])

def create_new_key(tmsg, token, issue_id=None):
    """
    Creates and sends new key for the user and

    :param tmsg: Telegram message
    :param token: Telegram bot token
    :param issue_id: User's issue connecting to server
    """
    try:
        new_key = api.get_new_key(user_id=tmsg.user_uid, user_issue=issue_id)
    except Exception as exc:
        logger.error(f'Error in creating new key {exc}')
        telegram.send_message(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_ERROR'))
        return None
    if not new_key:
        telegram.send_message(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_ERROR'))
    else:

        awsurl = (CONFIG['OUTLINE_AWS_URL'].format(
            urllib.parse.quote(new_key)))
        telegram.send_message(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_NEW_KEY_A').format(awsurl),
            parse='MARKDOWN')
        telegram.send_message(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_NEW_KEY_B'),
            parse='MARKDOWN')
        telegram.send_message(
            token,
            tmsg.chat_id,
            new_key)

def bot_handler(event, _):
    """
    Main entry point to handle the bot

    param event: information about the chat
    :param _: information about the telegram message (unused)
    """
    logger.info(
        "%s:%s Request received:%s",
        __name__,
        str(time.time()),
        str(event))

    try:
        default_language = event["lang"]
        logger.info("Language is %s", event["lang"])
    except KeyError:
        default_language = "fa"
        logger.info("Language is not defined!")

    try:
        token = event['token']
    except KeyError:
        logger.error("Token is not defined!")
        return None

    try:
        tmsg = TelegramMessage(event, default_language)
        logger.info("TMSG object: {}".format(tmsg))
    except Exception as exc:
        logger.error(
            'Error in Telegram Message parsing {} {}'.format(event, str(exc)))
        return None

    preferred_lang = dynamodb.get_user_lang(
        table=CONFIG["DYNAMO_TABLE"],
        chat_id=tmsg.chat_id)
    if (preferred_lang is None or
            preferred_lang not in CONFIG['SUPPORTED_LANGUAGES']):
        preferred_lang = default_language
    current_language = CONFIG['SUPPORTED_LANGUAGES'].index(preferred_lang)
    logger.info('User language is {}'.format(preferred_lang))

    change_lang(preferred_lang)
    tmsg.lang = preferred_lang

    if tmsg.body == globalvars.lang.text('MENU_BACK_HOME'):
        telegram.send_keyboard(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_HOME_ELSE'),
            globalvars.HOME_KEYBOARD)
        save_chat_status(tmsg.chat_id, STATUSES['HOME'])
        return

    if tmsg.command == CONFIG['TELEGRAM_START_COMMAND'] and len(tmsg.command_arg) > 0:
        tmsg.command = ""
        tmsg.body = base64.urlsafe_b64decode(tmsg.command_arg)

    # Check for commands (starts with /)
    if tmsg.command == CONFIG["TELEGRAM_START_COMMAND"]:
        dynamodb.create_chat_status(CONFIG['DYNAMO_TABLE'], tmsg.chat_id, STATUSES['START'])
        telegram.send_message(
            token,
            tmsg.chat_id,
            globalvars.lang.text("MSG_INITIAL_SCREEN").format(CONFIG['VERSION']))
        keyboard = make_language_keyboard()
        telegram.send_keyboard(
            token,
            tmsg.chat_id,
            globalvars.lang.text('MSG_SELECT_LANGUAGE'),
            keyboard)
        save_chat_status(tmsg.chat_id, STATUSES['SET_LANGUAGE'])
        return None
    elif tmsg.command == CONFIG['TELEGRAM_ADMIN_COMMAND']:
        chat_status = int(dynamodb.get_chat_status(
            table=CONFIG["DYNAMO_TABLE"],
            chat_id=tmsg.chat_id))
        if not admin_menu(token, tmsg, chat_status):
            telegram.send_keyboard(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_HOME'),
                globalvars.HOME_KEYBOARD
            )
        return None

    # non-command texts
    elif tmsg.command == '':  # This is a message not started with /
        chat_status = int(dynamodb.get_chat_status(
            table=CONFIG["DYNAMO_TABLE"],
            chat_id=tmsg.chat_id))

        if chat_status >= STATUSES['ADMIN_SECTION_HOME']:
            if not admin_menu(token, tmsg, chat_status):
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME'),
                    globalvars.HOME_KEYBOARD
                )
            return None

        elif chat_status == STATUSES['SET_LANGUAGE']:
            if (tmsg.body is None or
                    tmsg.body not in globalvars.lang.text('SUPPORTED_LANGUAGES')):
                message = globalvars.lang.text('MSG_LANGUAGE_CHANGE_ERROR')
            else:
                new_lang = CONFIG['SUPPORTED_LANGUAGES'][globalvars.lang.text(
                    'SUPPORTED_LANGUAGES').index(tmsg.body)]
                dynamodb.save_user_lang(
                    table=CONFIG["DYNAMO_TABLE"],
                    chat_id=tmsg.chat_id,
                    language=new_lang)
                change_lang(new_lang)
                message = globalvars.lang.text('MSG_LANGUAGE_CHANGED').format(tmsg.body)
            telegram.send_message(
                token,
                tmsg.chat_id,
                message)

            try:
                user_exist = api.get_user(tmsg.user_uid)
            except Exception:
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_ERROR'))
                return None

            if not user_exist:
                choices, a, b = get_choice(
                    table=CONFIG["DYNAMO_TABLE"],
                    chat_id=tmsg.chat_id)
                if choices:
                    keyboard = telegram.make_keyboard(choices, 2, '')
                    telegram.send_keyboard(
                        token,
                        tmsg.chat_id,
                        "{}\n{} + {}:".format(globalvars.lang.text("MSG_ASK_CAPTCHA"), a, b),
                        keyboard)
                save_chat_status(tmsg.chat_id, STATUSES['FIRST_CAPTCHA'])
            else:
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME_ELSE'),
                    globalvars.HOME_KEYBOARD)
                save_chat_status(tmsg.chat_id, STATUSES['HOME'])
            return None

        elif chat_status == STATUSES['FIRST_CAPTCHA']:
            check = check_captcha(
                table=CONFIG["DYNAMO_TABLE"],
                chat_id=tmsg.chat_id,
                sum=int(tmsg.body))
            if check:
                tos = get_tos_link()
                pp = get_pp_link()
                if tos is not None:
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        tos
                    )
                if pp is not None:
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        pp
                    )
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text("MSG_OPT_IN"),
                    globalvars.OPT_IN_KEYBOARD)
                save_chat_status(tmsg.chat_id, STATUSES['OPT_IN'])
            else:
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_WRONG_CAPTCHA'))
                choices, a, b = get_choice(
                    table=CONFIG["DYNAMO_TABLE"],
                    chat_id=tmsg.chat_id)
                if choices:
                    keyboard = telegram.make_keyboard(choices, 2, '')
                    telegram.send_keyboard(
                        token,
                        tmsg.chat_id,
                        "{}\n{} + {}:".format(globalvars.lang.text("MSG_ASK_CAPTCHA"), a, b),
                        keyboard)
                save_chat_status(tmsg.chat_id, STATUSES['FIRST_CAPTCHA'])
            return None

        elif chat_status == STATUSES['OPT_IN']:
            if tmsg.body == globalvars.lang.text('MENU_PRIVACY_POLICY_CONFIRM'):
                try:
                    api.create_user(user_id=tmsg.user_uid)
                except Exception:
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_ERROR'))
                    return None
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME'),
                    globalvars.HOME_KEYBOARD)
                save_chat_status(tmsg.chat_id, STATUSES['HOME'])
            else:
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_PRIVACY_POLICY_DECLINE'),
                    globalvars.OPT_IN_DECLINED_KEYBOARD)
                save_chat_status(tmsg.chat_id, STATUSES['OPT_IN_DECLINED'])
            return None

        elif chat_status == STATUSES['OPT_IN_DECLINED']:
            if tmsg.body == globalvars.lang.text('MENU_BACK_PRIVACY_POLICY'):
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text("MSG_OPT_IN"),
                    globalvars.OPT_IN_KEYBOARD)
                save_chat_status(tmsg.chat_id, STATUSES['OPT_IN'])
            elif tmsg.body == globalvars.lang.text('MENU_HOME_CHANGE_LANGUAGE'):
                keyboard = make_language_keyboard()
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_SELECT_LANGUAGE'),
                    keyboard)
                save_chat_status(tmsg.chat_id, STATUSES['SET_LANGUAGE'])
            return None

        elif chat_status == STATUSES['HOME']:
            if tmsg.body == globalvars.lang.text('MENU_HOME_EXISTING_KEY'):
                try:
                    user_exist = api.get_user(tmsg.user_uid)
                except Exception:
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_ERROR'))
                    return None

                if not user_exist:
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_NO_ACCOUNT'),
                        parse='MARKDOWN')
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        '/start')
                    return None
                elif not user_exist['outline_key']:
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_NO_EXISTING_KEY'))
                else:
                    awsurl = (CONFIG['OUTLINE_AWS_URL'].format(urllib.parse.quote(user_exist['outline_key'])))
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_EXISTING_KEY_A').format(awsurl),
                        parse='MARKDOWN')
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_EXISTING_KEY_B'),
                        parse='MARKDOWN')
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        user_exist['outline_key'])

                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME_ELSE'),
                    globalvars.HOME_KEYBOARD)
                save_chat_status(tmsg.chat_id, STATUSES['HOME'])
                return None
            elif tmsg.body == globalvars.lang.text('MENU_CHECK_STATUS'):
                blocked = False
                banned = False
                try:
                    user_info = api.get_outline_user(tmsg.user_uid)
                    vpnuser = api.get_user(tmsg.user_uid)
                except Exception:
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_ERROR'))
                    return None
                banned = vpnuser['banned']
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_ACCOUNT_INFO_BANNED') \
                        if banned else globalvars.lang.text('MSG_ACCOUNT_INFO_OK')
                )
                if not banned:
                    if user_info is not None:
                        try:
                            serverinfo = api.get_outline_server_info(user_info['server'])

                        except Exception:
                            telegram.send_message(
                                token,
                                tmsg.chat_id,
                                globalvars.lang.text('MSG_ERROR'))
                            return None

                    if serverinfo is not None:
                        blocked = serverinfo['is_blocked']
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_SERVER_INFO_BLOCKED') \
                            if blocked else globalvars.lang.text('MSG_SERVER_INFO_OK')
                    )
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME_ELSE'),
                    globalvars.HOME_KEYBOARD)
                return None
            elif tmsg.body == globalvars.lang.text('MENU_HOME_NEW_KEY'):
                try:
                    user_exist = api.get_user(tmsg.user_uid)
                except Exception:
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_ERROR'))
                    return None

                if not user_exist:
                    logger.info("New user: {}".format(tmsg.user_uid))
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_NO_ACCOUNT'),
                        parse='MARKDOWN')
                    telegram.send_message(
                        token,
                        tmsg.chat_id,
                        '/start')
                    return None
                elif not user_exist['outline_key']:
                    create_new_key(tmsg, token)
                    telegram.send_keyboard(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_HOME_ELSE'),
                        globalvars.HOME_KEYBOARD)
                    save_chat_status(tmsg.chat_id, STATUSES['HOME'])
                    return None

                issues_dict = api.get_issues(tmsg.lang)
                issues = list(issues_dict.values())
                keyboard = telegram.make_keyboard(issues, 2, '')
                telegram.send_keyboard(
                    token, tmsg.chat_id,
                    globalvars.lang.text("MSG_ASK_ISSUE"),
                    keyboard)
                save_chat_status(tmsg.chat_id, STATUSES['ASK_ISSUE'])
                return None

            elif tmsg.body == globalvars.lang.text('MENU_HOME_FAQ'):
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_FAQ_URL'))
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME_ELSE'),
                    globalvars.HOME_KEYBOARD)
                return None

            elif tmsg.body == globalvars.lang.text('MENU_HOME_INSTRUCTION'):
                photo_name = ""
                with open(photo_name, 'rb') as photofile:
                    telegram.send_photo(
                        token,
                        tmsg.chat_id,
                        photofile.read(),
                        "instructions")
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME_ELSE'),
                    globalvars.HOME_KEYBOARD)
                return None

            elif tmsg.body == globalvars.lang.text('MENU_HOME_CHANGE_LANGUAGE'):
                keyboard = make_language_keyboard()
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_SELECT_LANGUAGE'),
                    keyboard)
                save_chat_status(tmsg.chat_id, STATUSES['SET_LANGUAGE'])
                return None

            elif tmsg.body == globalvars.lang.text('MENU_HOME_PRIVACY_POLICY'):
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    get_pp_link())
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME_ELSE'),
                    globalvars.HOME_KEYBOARD)
                return None

            elif tmsg.body == globalvars.lang.text('MENU_HOME_SUPPORT'):
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text("MSG_SUPPORT_BOT"))
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    CONFIG["SUPPORT_BOT"])
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME_ELSE'),
                    globalvars.HOME_KEYBOARD)
                return None

            elif tmsg.body == globalvars.lang.text('MENU_HOME_DELETE_ACCOUNT'):
                keyboard = telegram.make_keyboard(
                    globalvars.lang.text('MENU_DELETE_REASONS'),
                    2,
                    globalvars.lang.text('MENU_BACK_HOME'))
                telegram.send_keyboard(
                    token, tmsg.chat_id,
                    globalvars.lang.text("MSG_ASK_DELETE_REASONS"),
                    keyboard)
                save_chat_status(tmsg.chat_id, STATUSES['DELETE_ACCOUNT_REASON'])
                return None

        elif chat_status == STATUSES['ASK_ISSUE']:
            issues_dict = api.get_issues(tmsg.lang)
            issue_ids = [key for (key, value) in issues_dict.items() if value == tmsg.body]
            if not issue_ids:
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text("MSG_UNSUPPORTED_COMMAND"))
            else:
                create_new_key(tmsg, token, issue_ids[0])

            telegram.send_keyboard(
                token,
                tmsg.chat_id,
                globalvars.lang.text('MSG_HOME_ELSE'),
                globalvars.HOME_KEYBOARD)
            save_chat_status(tmsg.chat_id, STATUSES['HOME'])
            return None

        elif chat_status == STATUSES['DELETE_ACCOUNT_REASON']:
            if tmsg.body in globalvars.lang.text('MENU_DELETE_REASONS'):
                reason_id = globalvars.lang.text('MENU_DELETE_REASONS').index(tmsg.body)
                logger.debug('user {} wants to delete her account because {}'.format(
                    tmsg.user_uid,
                    tmsg.body
                ))
                try:
                    deleted = api.delete_user(user_id=tmsg.user_uid)
                except Exception:
                    telegram.send_keyboard(
                        token,
                        tmsg.chat_id,
                        globalvars.lang.text('MSG_ERROR'),
                        globalvars.HOME_KEYBOARD)
                    return None
                if deleted:
                    telegram.send_keyboard(
                        token, tmsg.chat_id,
                        globalvars.lang.text("MSG_DELETED_ACCOUNT"),
                        globalvars.BACK_TO_HOME_KEYBOARD)
                    save_chat_status(tmsg.chat_id, STATUSES['DELETE_ACCOUNT_CONFIRM'])
                return None

        else:  # unsupported message from user
            telegram.send_message(
                token,
                tmsg.chat_id,
                globalvars.lang.text("MSG_UNSUPPORTED_COMMAND"))

            try:
                user_exist = api.get_user(tmsg.user_uid)
            except Exception:
                telegram.send_message(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_ERROR'))
                return None
            if not user_exist:  # start from First step
                keyboard = make_language_keyboard()
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_SELECT_LANGUAGE'),
                    keyboard)
                save_chat_status(tmsg.chat_id, STATUSES['SET_LANGUAGE'])
                return None
            else:
                telegram.send_keyboard(
                    token,
                    tmsg.chat_id,
                    globalvars.lang.text('MSG_HOME_ELSE'),
                    globalvars.HOME_KEYBOARD)
                save_chat_status(tmsg.chat_id, STATUSES['HOME'])
            return None
