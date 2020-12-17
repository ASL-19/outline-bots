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

from errors import ValidationError


def parse_ses_notification(ses_notification):
    """ 
    Gather incoming email info and validate

    :param ses_notification: ses object from Lambda event
    :return: source_email, recipient
    """
    if ses_notification['receipt']['spamVerdict']['status'] == 'FAIL':
        raise ValidationError('Email flagged as spam. EMAIL={}'.format(
            ses_notification['mail']['source']))

    if ses_notification['receipt']['virusVerdict']['status'] == 'FAIL':
        raise ValidationError('Email contains virus. EMAIL={}'.format(
            ses_notification['mail']['source']))

    source_email = ses_notification['mail']['source']
    recipient = ses_notification['mail']['destination'][0].lower()
    return (source_email, recipient)
