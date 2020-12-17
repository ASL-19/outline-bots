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

""" Email Responder Lambda Function """

import logging
import api
from botocore.exceptions import ClientError
import feedback
from ses import parse_ses_notification
from settings import CONFIG
from template import TEMPLATES
import urllib.parse
import jinja2


logger = logging.getLogger()
logger.setLevel(CONFIG['LOG_LEVEL'])


def render_template(template, **kwargs):
    """
    Renders a Jinja template into HTML

    :param template: name of the template
    :param kwargs: values for template
    :return: rendered template
    """

    template_loader = jinja2.FileSystemLoader(searchpath="templates/")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template)
    return template.render(**kwargs)


def email(source_email, template_name):
    """
    Send 'No server' email

    :param source_email: From email address
    :param template_name: Template to use for the email
    :return: True when successful False otherwise
    """
    try:
        feedback.send_email(
            CONFIG['REPLY_EMAIL'],
            source_email,
            TEMPLATES['EMAIL_SUBJECT'],
            TEMPLATES['NOSERVER_TEXT_BODY'].format(
                DELETE_USER_EMAIL=CONFIG['DELETE_USER_EMAIL'],
                GET_EMAIL=CONFIG['GET_EMAIL']),
            render_template(template_name,
                            DELETE_USER_EMAIL=CONFIG['DELETE_USER_EMAIL'],
                            GET_EMAIL=CONFIG['GET_EMAIL']),
            '',
            None,
            CONFIG['FEEDBACK_EMAIL'])
        return True
    except ClientError as error:
        logger.error('Error sending email: %s', str(error))
        feedback.send_email(
            CONFIG['REPLY_EMAIL'],
            source_email,
            TEMPLATES['EMAIL_SUBJECT'],
            TEMPLATES['TRY_AGAIN_TEXT_BODY'].format(
                DELETE_USER_EMAIL=CONFIG['DELETE_USER_EMAIL']),
            render_template('try_again.j2',
                            DELETE_USER_EMAIL=CONFIG['DELETE_USER_EMAIL']),
            '',
            None,
            CONFIG['FEEDBACK_EMAIL'])
        return False


def email_key(source_email, awsurl):
    """
    Send 'New key' email

    :param source_email: From email address
    :param awsurl: AWS URL for the invitation page
    :return: True when successful False otherwise
    """
    try:
        feedback.send_email(
            CONFIG['REPLY_EMAIL'],
            source_email,
            TEMPLATES['EMAIL_SUBJECT'],
            TEMPLATES['OUTLINE_NEW_TEXT_BODY'].format(
                DELETE_USER_EMAIL=CONFIG['DELETE_USER_EMAIL'],
                key=awsurl),
            render_template('outline_new.j2',
                            key=awsurl,
                            SUPPORT_EMAIL=CONFIG['SUPPORT_EMAIL'],
                            DELETE_USER_EMAIL=CONFIG['DELETE_USER_EMAIL']),
            '',
            None,
            CONFIG['FEEDBACK_EMAIL'])
        return True
    except ClientError as error:
        logger.error('Error sending email: %s', str(error))
        feedback.send_email(
            CONFIG['REPLY_EMAIL'],
            source_email,
            TEMPLATES['EMAIL_SUBJECT'],
            TEMPLATES['TRY_AGAIN_TEXT_BODY'].format(
                DELETE_USER_EMAIL=CONFIG['DELETE_USER_EMAIL']),
            render_template('try_again.j2',
                            DELETE_USER_EMAIL=CONFIG['DELETE_USER_EMAIL']),
            '',
            None,
            CONFIG['FEEDBACK_EMAIL'])
        return False


def mail_responder(event, _):
    """
    Main entry point to handle the feedback form
    :param event: information about the email
    :return: True when successful, False otherwise
    """
    logger.info('%s: Request received:%s', __name__,
                str(event['Records'][0]['eventSource']))

    try:
        (source_email, recipient) = parse_ses_notification(
            event['Records'][0]['ses'])
    except Exception:
        logger.error('Error parsing received Email')
        return False

    LANG = CONFIG['LANG']

    logger.debug('Source Email {} recipient {}'.format(
        source_email, recipient))

    if recipient == CONFIG['TEST_EMAIL']:
        feedback.send_email(
            CONFIG['REPLY_EMAIL'],
            source_email,
            TEMPLATES['EMAIL_SUBJECT'],
            'a',
            'a',
            '',
            None,
            CONFIG['FEEDBACK_EMAIL'])
        return True

    elif recipient == CONFIG['TEST_EMAIL_NEW']:
        email_key(source_email, 'https://example.com')
        return True

    elif recipient == CONFIG['REPLY_EMAIL']:
        logger.info('Response to no-reply ignored')
        return True

    elif recipient == CONFIG['DELETE_USER_EMAIL']:
        try:
            deleted = api.delete_user(user_id=source_email)
        except Exception:
            email(source_email, 'try_again.j2')
            return False
        if deleted:
            email(source_email, 'unsubscribed.j2')
            return False

    elif recipient == CONFIG['GET_EMAIL']:
        try:
            user_exist = api.get_user(source_email)
        except Exception:
            logger.error('API error when checking {}'.format(source_email))
            email(source_email, 'try_again.j2')
            return False

        if not user_exist:
            try:
                api.create_user(source_email, 'EM')
            except Exception:
                logger.error('API error when Creating {}'.format(source_email))
                email(source_email, 'try_again.j2')
                return False

        try:
            new_key = api.get_new_key(user_id=source_email)
        except Exception:
            logger.error(
                'API error when getting key fo {}'.format(source_email))
            email(source_email, 'try_again.j2')
            return False

        if not new_key:
            email(source_email, 'no_key.j2')
            return False

        awsurl = ((CONFIG['OUTLINE_AWS_URL']).format(
            urllib.parse.quote(new_key)))

        email_key(source_email, awsurl)

    return True
