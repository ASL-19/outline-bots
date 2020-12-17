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
logger = logging.getLogger()


class ObjectCreationFailed(Exception):
    pass


class TelegramMessage(object):

    def __init__(self, event, lang):

        self.lang = lang
        self.command = ''
        self.command_arg = ''

        if 'message' in event['Input']:
            self.type = 'MESSAGE'
            message = event['Input']['message']
            if message['chat']['type'] == 'supergroup':
                logger.info("Message from a Telegram Group: {}".format(
                    message['chat']['title']))
                raise ObjectCreationFailed
            elif message['chat']['type'] == 'channel':
                logger.info("Forwarded from a Telegram Channel by: {}".format(
                    message['chat']['username']))
                raise ObjectCreationFailed
            try:
                self.msg_date = message['date']
                self.id = int(message['message_id'])
                self.chat_id = int(message['chat']['id'])
                self.user_uid = str(message['from']['id'])
                if 'from' in message:
                    if 'username' in message['from']:
                        self.user_id = str(message['from']['username'])
                    else:
                        self.user_id = str(message['from']['id'])
                    self.user_info = str(message['from'])
                else:
                    self.user_id = u''
                    self.user_info = u''

                if 'text' in message:
                    self.body = message['text']
                    self.bodytype = 'TEXT'
                elif 'document' in message:
                    self.body = message['document']['file_id']
                    self.bodytype = 'DOCUMENT'
                    self.bodymime = message['document']['mime_type']
                else:
                    self.body = ''
                    self.bodytype = 'UNKNOWN'

            except Exception as exc:
                logger.error(str(exc))
                raise ObjectCreationFailed

        elif 'inline_query' in event['Input']:
            self.type = 'INLINE'
            inline_query = event['Input']['inline_query']
            try:
                self.id = inline_query['id']
                self.chat_id = inline_query['from']['id']
                self.user_id = inline_query['from']['username']
                self.body = inline_query['query']
                self.is_bot = inline_query['from']['is_bot']

            except Exception as exc:
                raise ObjectCreationFailed

        elif 'edited_message' in event['Input']:
            self.type = 'MESSAGE'
            message = event['Input']['edited_message']
            try:
                self.msg_date = message['edit_date']
                self.id = int(message['message_id'])
                self.chat_id = int(message['chat']['id'])
                self.user_uid = str(message['from']['id'])
                if 'from' in message:
                    if 'username' in message['from']:
                        self.user_id = str(message['from']['username'])
                    else:
                        self.user_id = str(message['from']['id'])
                    self.user_info = str(message['from'])
                else:
                    self.user_id = u''
                    self.user_info = u''

                self.body = message['text']

            except Exception as exc:
                logger.error(str(exc))
                raise ObjectCreationFailed

        elif 'callback_query' in event['Input']:
            self.type = 'CALLBACK'
            callback_query = event['Input']['callback_query']
            try:
                self.id = callback_query['id']
                if 'message' in callback_query and 'chat' in callback_query['message']:
                    self.chat_id = callback_query['message']['chat']['id']
                else:
                    self.chat_id = callback_query['from']['id']

                if 'message' in callback_query:
                    self.msg_id = callback_query['message']['message_id']
                    self.inline = False
                else:
                    self.msg_id = callback_query['inline_message_id']
                    self.inline = True

                self.user_uid = str(message['from']['id'])
                if 'username' in callback_query['from']:
                    self.user_id = callback_query['from']['username']
                else:
                    self.user_id = callback_query['from']['id']

                self.firstname = callback_query['from']['first_name']
                self.body = callback_query['data']

            except Exception as exc:
                raise ObjectCreationFailed

        else:
            logger.error('Undefined message type!')
            raise ObjectCreationFailed

        if self.body[0] == '/':
            self.command = self.body[1:]
            cmd = self.command.split(' ', 1)
            if len(cmd) > 1:
                self.command = str(cmd[0])
                self.command_arg = str(cmd[1])
            self.command = self.command.lower()
