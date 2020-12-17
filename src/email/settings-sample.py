# coding=UTF8
"""
Settings file for email responder
"""
import logging
import os
# __file__ refers to the file settings.py
CONFIG = {
    'LANG': '',
    'VERSION': '0.1.0',
    # refers to application_top
    'APP_PATH': os.path.dirname(os.path.abspath(__file__)),
    'MAX_ATTACHMENT_SIZE': 0,    # max size in bytes of attachment
    'LOG_LEVEL': logging.INFO,

    'TEST_EMAIL': 'test_me@$EMAIL_DOMAIN',
    'TEST_EMAIL_NEW': 'test_me_new@$EMAIL_DOMAIN',
    'DELETE_USER_EMAIL': 'unsubscribe@$EMAIL_DOMAIN',
    'REPLY_EMAIL': 'no-reply@$EMAIL_DOMAIN',
    'GET_EMAIL': 'get@$EMAIL_DOMAIN',
    'FEEDBACK_EMAIL': 'feedback@$EMAIL_DOMAIN',
    'SUPPORT_EMAIL': 'support@$EMAIL_DOMAIN',
    'INSTRUCTION_URL': '$INSTRUCTION_URL',

    'API_KEY': '$API_KEY',
    'API_URL': '$API_URL',
    'OUTLINE_AWS_URL': 'https://s3.amazonaws.com/outline-vpn/invite.html#{}',
    'OUTLINE_GUIDELINE_PHOTO': {
        'en': '',
        'fa': '',
        'ar': ''
    },
}
