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
import boto3
import hashlib
from botocore.exceptions import ClientError

logger = logging.getLogger()

def save_info_link(
        table,
        link,
        language,
        linktype):
    """
    Save the users' preferred language to the DB

    :param table: DynamoDB Table Name
    :param link: Link to be saved
    :param language: User's preferred language
    :param linktype: What is the nature of link to save
    :return: True in case of success and False otherwise
    """
    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        ddtable.update_item(
            Key={
                'language': language,
                'linktype': linktype
            },
            UpdateExpression='SET link = :element',
            ExpressionAttributeValues={
                ':element': link
            })
    except ClientError as error:
        logger.error(
            '[save_info_link] Unable to write to {}: {}'.format(table, str(error)))
        return False

    return True


def get_info_link(
    table,
    language,
    linktype):
    """
    Retrieves the status of chat that is saved in the
    DB.

    :param table: DynamoDB Table Name
    :param language: User's preferred language
    :param linktype: What is the nature of link to return
    :return: Link or None in case of error
    """
    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        result = ddtable.get_item(
            ConsistentRead=True,
            Key={
                'language': language,
                'linktype': linktype
            })
    except ClientError as error:
        logger.error(
            '[get_info_link] Unable to read from {}: {}'.format(table, str(error)))
        return None

    logger.info('Result from Query is {}'.format(str(result)))

    if 'Item' not in result:
        return None

    if len(result['Item']) == 0:
        return None

    return result['Item']['link']


def save_user_lang(
        table,
        chat_id,
        language):
    """
    Save the users' preferred language to the DB

    :param table: DynamoDB Table Name
    :param user_id: Telegram User ID
    :param chat_id: Telegram Chat ID
    :param language: User's preferred language
    :return: True in case of success and False otherwise
    """
    chat_hash = hashlib.sha512(str(chat_id).encode('utf-8')).hexdigest()

    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        ddtable.update_item(
            Key={
                'chat_id': str(chat_hash)
            },
            UpdateExpression='SET #lang = :element',
            ExpressionAttributeValues={
                ':element': str(language)},
            ExpressionAttributeNames={
                "#lang": "language"
            })
    except ClientError as error:
        logger.error(
            '[save_user_lang] Unable to read from {}: {}'.format(table, str(error)))
        return False

    return True


def create_chat_status(
        table,
        chat_id,
        status):
    """
    Save the users' preferred language to the DB

    :param table: DynamoDB Table Name
    :param user_id: Telegram User ID
    :param chat_id: Telegram Chat ID
    :param status: chat status
    :return: True in case of success and False otherwise
    """
    chat_hash = hashlib.sha512(str(chat_id).encode('utf-8')).hexdigest()

    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)

    try:
        result = ddtable.get_item(
            ConsistentRead=True,
            Key={
                'chat_id': str(chat_hash)
            })
    except ClientError as error:
        logger.error(
            '[get_chat_status] Unable to read from {}: {}'.format(table, str(error)))
        return None

    if 'Item' not in result:
        try:
            ddtable.put_item(
                Item={
                    'chat_id': str(chat_hash),
                    'status': str(status),
                    'language': 'en',
                    'captcha': ['1', '2']})
        except ClientError as error:
            logger.error(
                '[create_chat_status] Unable to write to {}: {}'.format(table, str(error)))
            return False
        return True

    saved = save_chat_status(table, chat_id, status)
    if saved:
        return True
    return False


def save_chat_status(
        table,
        chat_id,
        status):
    """
    Retrieves the status of chat that is saved in the
    DB and add a list of captcha choices.

    :param table: DynamoDB Table Name
    :param chat_id: Telegram Chat ID
    :param status: chat status
    :return: True or False in case of failure
    """
    chat_hash = hashlib.sha512(str(chat_id).encode('utf-8')).hexdigest()

    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        ddtable.update_item(
            Key={
                'chat_id': str(chat_hash)
            },
            UpdateExpression='SET #st = :val',
            ExpressionAttributeValues={
                ':val': str(status)
            },
            ExpressionAttributeNames={
                "#st": "status"
            })
    except ClientError as error:
        logger.error(
            '[save_chat_status] Unable to read from {}: {}'.format(table, str(error)))
        return False

    return True


def get_chat_status(
        table,
        chat_id):
    """
    Retrieves the status of chat that is saved in the
    DB.

    :param table: DynamoDB Table Name
    :param user_id: Telegram User ID
    :param chat_id: Telegram Chat ID
    :return: chat status or None in case of error
    """
    chat_hash = hashlib.sha512(str(chat_id).encode('utf-8')).hexdigest()

    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        result = ddtable.get_item(
            ConsistentRead=True,
            Key={
                'chat_id': str(chat_hash)
            })
    except ClientError as error:
        logger.error(
            '[get_chat_status] Unable to read from {}: {}'.format(table, str(error)))
        return None

    if 'Item' not in result:
        return None

    if len(result['Item']) == 0:
        return None

    return result['Item']['status']


def save_user_lang(
        table,
        chat_id,
        language):
    """
    Save the users' preferred language to the DB

    :param table: DynamoDB Table Name
    :param user_id: Telegram User ID
    :param chat_id: Telegram Chat ID
    :param language: User's preferred language
    :return: True in case of success and False otherwise
    """
    chat_hash = hashlib.sha512(str(chat_id).encode('utf-8')).hexdigest()

    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        ddtable.update_item(
            Key={
                'chat_id': str(chat_hash)
            },
            UpdateExpression='SET #lang = :element',
            ExpressionAttributeValues={
                ':element': str(language)},
            ExpressionAttributeNames={
                "#lang": "language"
            })
    except ClientError as error:
        logger.error(
            '[save_user_lang] Unable to read from {}: {}'.format(table, str(error)))
        return False

    return True


def get_user_lang(
        table,
        chat_id):
    """
    Retrieves the status of chat that is saved in the DB.

    :param table: DynamoDB Table Name
    :param user_id: Telegram User ID
    :param chat_id: Telegram Chat ID
    :return: Language or None in case of error
    """
    chat_hash = hashlib.sha512(str(chat_id).encode('utf-8')).hexdigest()

    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        result = ddtable.get_item(
            ConsistentRead=True,
            Key={
                'chat_id': str(chat_hash)
            })
    except ClientError as error:
        logger.error(
            '[get_user_lang] Unable to read from {}: {}'.format(table, str(error)))
        return None

    logger.info('Result from Query is {}'.format(str(result)))

    if 'Item' not in result:
        return None

    if len(result['Item']) == 0:
        return None

    return result['Item']['language']


def save_captcha(
        table,
        chat_id,
        choices):
    """
    Retrieves the status of chat that is saved in the
    DB and add a list of captcha choices.

    :param table: DynamoDB Table Name
    :param chat_id: Telegram Chat ID
    :param choices: Captcha numbers
    :return: True or False in case of failure
    """
    chat_hash = hashlib.sha512(str(chat_id).encode('utf-8')).hexdigest()

    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        ddtable.update_item(
            Key={
                'chat_id': str(chat_hash)
            },
            UpdateExpression='SET #cpt = :element',
            ExpressionAttributeValues={
                ':element': choices},
            ExpressionAttributeNames={
                "#cpt": "captcha"
            })
    except ClientError as error:
        logger.error(
            '[save_captcha] Unable to read from {}: {}'.format(table, str(error)))
        return False

    return True


def get_captcha(
        table,
        chat_id):
    """
    Retrieves the status of chat that is saved in the DB.

    :param table: DynamoDB Table Name
    :param user_id: Telegram User ID
    :param chat_id: Telegram Chat ID
    :return: Captcha choices or None in case of error
    """
    chat_hash = hashlib.sha512(str(chat_id).encode('utf-8')).hexdigest()

    resource = boto3.resource('dynamodb')
    ddtable = resource.Table(table)
    try:
        result = ddtable.get_item(
            ConsistentRead=True,
            Key={
                'chat_id': str(chat_hash)
            })
    except ClientError as error:
        logger.error(
            '[get_captcha] Unable to read from {}: {}'.format(table, str(error)))
        return None

    logger.info('Result from Query is {}'.format(str(result)))

    if 'Item' not in result:
        return None

    if len(result['Item']) == 0:
        return None

    return result['Item']['captcha']
