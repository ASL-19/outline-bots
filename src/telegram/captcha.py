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
from dynamodb import save_captcha, get_captcha
from random import randint
import random

logger = logging.getLogger()

def get_choice(table, chat_id):
    """
    Generate a simple addition test with 4 answers

    :param table: Table name to save the captcha to
    :param chat_id: Telegram chat ID
    :return: numbers to be added and 3 random numbers and the answer
    """
    a = randint(1, 10)
    b = randint(1, 10)
    choices = random.sample(range(0, 20), 4)
    x = randint(0, 3)
    choices[x] = a + b
    if save_captcha(table, chat_id, [str(a), str(b)]):
        strchoices = [str(x) for x in choices]
        return strchoices, str(a), str(b)
    return None, None, None


def check_captcha(table, chat_id, sum):
    """
    A simple test to check if the user is a bot

    :param table: Table name to save the captcha to
    :param chat_id: Telegram chat ID
    :param sum: Sum of the numbers
    :return: True if it passed, False otherwise
    """
    choices = get_captcha(table, chat_id)
    if choices and sum == (int(choices[0]) + int(choices[1])):
        return True
    else:
        return False
