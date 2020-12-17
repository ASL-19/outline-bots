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

TEMPLATES = {
    'EMAIL_SUBJECT': """
            Hi!
        """,
    'OUTLINE_NEW_TEXT_BODY': """
            Dear User,

            Welcome to Outline VPN server distribution system. By receiving this email you accepted that you opt-in to our "Distribution list". ‌For more information about privacy policy please visit our website.
            *You can unsubscribe (mailto:{DELETE_USER_EMAIL}) at anytime if you wish, but you'll lose your server!

            Click on the following button to install Outline and get your personal access key to a server: {key}

        """,
    'NOSERVER_TEXT_BODY': """
            Dear User,

            There is no access key available at the moment.
            If you have any questions or concerns, you can contact our support channels through Telegram or Email.
            You can unsubscribe (mailto:{DELETE_USER_EMAIL}) at anytime if you wish, but you'll lose your server!

            Thank you for your patience!

        """,
    'TRY_AGAIN_TEXT_BODY': """
            Dear User,

            Something went wrong!
            Please try again by sending an to {GET_EMAIL}
            You can unsubscribe (mailto:{DELETE_USER_EMAIL}) at anytime if you wish, but you'll lose your server!

            Thank you for your patience!

        """,
    'UNSUBSCRIBED_TEXT_BODY': """
            You unsubscribed from our mailing list, and your access key is revoked now.
            You can always subscribe back and get a new access key by just sending an email to {GET_EMAIL}


            Thank you!

        """
}
