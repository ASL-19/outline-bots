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

"""
Holds local library error types 
"""

class PyskoochehException(Exception):
    """ Base class for exceptions in Pyskoocheh """
    def __init__(self, value):
        """ Set value of error message """
        super(PyskoochehException, self).__init__()
        self.value = value
    def __str__(self):
        """ Output representation of error """
        return repr(self.value)

class AWSError(PyskoochehException):
    """ AWS API Error Wrapper """

class FeedbackError(PyskoochehException):
    """ Feedback Error Wrapper """

class TelegramError(PyskoochehException):
    """ Telegram Error Wrapper """

class ValidationError(PyskoochehException):
    """ Validation Error Wrapper """

class HTTPError(PyskoochehException):
    """ HTTP Error on Requests """

class DBError(PyskoochehException):
    """ DB Errors """
