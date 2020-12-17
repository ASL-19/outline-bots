""" Telegram Module

    Holds functions for working with Telegram API
"""
import time as systime
from datetime import datetime, time, timedelta, tzinfo
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import boto3
from botocore.exceptions import ClientError
from errors import AWSError, ValidationError, FeedbackError

def get_feedback_digest(table_name, days=1):
    """ Get website feedback and return records timezones are shifted to account for EST

    Args:
        table_name: name of dynamodb table to pull feedback from
        days: optional number of days (starting from yesterday) to return feedback for (default 1)
    Returns:
        set of feedback objects or false if empty
    Raises:
        AWSError: dynamodb scan failed
    """
    utc_timezone = UTC()
    eastern_timezone = USTimeZone(-5, "Eastern", "EST", "EDT")

    epoch = datetime(1970, 1, 1, tzinfo=utc_timezone)
    zero_time = time(0, 0, 0, 0, eastern_timezone)
    today = datetime.now(eastern_timezone)
    yesterday = today - timedelta(days)
    today = (datetime.combine(today, zero_time) - epoch).total_seconds()
    yesterday = (datetime.combine(yesterday, zero_time) - epoch).total_seconds()

    dynamodb = boto3.client('dynamodb')
    try:
        feedback = dynamodb.scan(
            TableName=table_name,
            FilterExpression='feedback_time BETWEEN :yesterday AND :today',
            ExpressionAttributeValues={
                ':yesterday': {'N': str(yesterday)},
                ':today': {'N': str(today)},
            })
    except ClientError as error:
        raise AWSError('DynamoDB Error: {}'.format(str(error)))

    if feedback['Count'] > 0:
        return feedback['Items']
    else:
        return False

def send_email(email_from, email_to, subject, text_body, html_body, file_name, file_data, src_email=None):
    """ Send email with text, html and attachment sections

    Args:
        email_from: address to send from
        email_to: address to send to
        subject: email subject line
        text_body: text/plain body of email
        html_body: text/html body of email, preferred display
        file_name: name of attachment file
        file_data: raw binary file data
    Returns:
        SES response object from AWS API
    Raises:
        FeedbackError: no body text provided or SES response is empty
    """
    # Compose email with link or binary
    sesclient = boto3.client('ses', region_name='us-east-1')
    msg = MIMEMultipart()
    msg['Subject'] = str(subject)
    msg['From'] = email_from
    msg['To'] = email_to
    if html_body and text_body:
        email_content = MIMEMultipart('alternative')
        email_content.attach(MIMEText(text_body, 'plain', 'UTF-8'))
        email_content.attach(MIMEText(html_body, 'html', 'UTF-8'))
        msg.attach(email_content)
    elif text_body:
        msg.attach(MIMEText(text_body, 'plain', 'UTF-8'))
    else:
        raise ValidationError('No body text found')

    # attachment must be last part or clients won't show it
    if file_data:
        part = MIMEApplication(file_data)
        part.add_header('Content-Disposition', 'attachment', filename=file_name)
        msg.attach(part)

    try:
        if src_email == None:
            response = sesclient.send_raw_email(RawMessage={'Data': msg.as_string()})
        else:
            response = sesclient.send_raw_email(Source=src_email,
                                                RawMessage={'Data': msg.as_string()})
    except ClientError as error:
        raise AWSError('SendMail UnknownError: {}'.format(str(error)))

    if response is None:
        raise FeedbackError('Unknown Error: Return Value is None')

    return response

def send_feedback(table_name, user_name, subject, message):
    """ Log feedback to website_feedback table

    Args:
        table_name: name of dynamodb table to pull feedback from
        user_name: unique id of user, username/email/uuid
        subject: string subject of user feedback
        message: string containing user feedback
    Returns:
        None
    Raises:
        AWSError: Could not write to database
    """
    dynamodb = boto3.client('dynamodb')
    try:
        dynamodb.put_item(
            TableName=table_name,
            Item={
                'feedback_time': {'N': str(systime.time())},
                'user_name': {'S': user_name},
                'subject': {'S': subject},
                'message': {'S': message},
            })
    except ClientError as error:
        raise AWSError('DynamoDB Error: {}'.format(str(error)))

def template_email_link(text_body, html_body, attachment_html, link):
    """ Template text and html body text assumes that static
        template placeholder {{link}} exists in attachment link

    Args:
        textBody: plain text version of email
        htmlBody: html version of email
        attachmentHtml: surrounding html to use for S3 link
        link: file url, if None then replace template string with ''
    Returns:
        (text_body, html_body) tuple of formatted text
    """

    if link:
        text_body += '\n\n' + link
        html_body += attachment_html.replace('{{link}}', link)
    return (text_body, html_body)

# Time zone definitions
# US DST Rules
class UTC(tzinfo):
    """UTC"""
    def utcoffset(self, _):
        return timedelta(0)

    def tzname(self, _):
        return "UTC"

    def dst(self, _):
        return timedelta(0)

class USTimeZone(tzinfo):
    """ USTimeZone """
    def __init__(self, hours, reprname, stdname, dstname):
        super(USTimeZone, self).__init__()
        self.stdoffset = timedelta(hours=hours)
        self.reprname = reprname
        self.stdname = stdname
        self.dstname = dstname

    def __repr__(self):
        return self.reprname

    @staticmethod
    def first_sunday_on_or_after(after_date):
        """ Return first sunday after after_date """
        days_to_go = 6 - after_date.weekday()
        if days_to_go:
            after_date += timedelta(days_to_go)
        return after_date

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstname
        else:
            return self.stdname

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        zero = timedelta(0)
        hour = timedelta(hours=1)
        # This is a simplified (i.e., wrong for a few cases) set of rules for US
        # DST start and end times. For a complete and up-to-date set of DST rules
        # and timezone definitions, visit the Olson Database (or try pytz):
        # http://www.twinsun.com/tz/tz-link.htm
        # http://sourceforge.net/projects/pytz/ (might not be up-to-date)
        #
        # In the US, since 2007, DST starts at 2am (standard time) on the second
        # Sunday in March, which is the first Sunday on or after Mar 8.
        dststart_2007 = datetime(1, 3, 8, 2)
        # and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
        dstend_2007 = datetime(1, 11, 1, 1)
        # From 1987 to 2006, DST used to start at 2am (standard time) on the first
        # Sunday in April and to end at 2am (DST time; 1am standard time) on the last
        # Sunday of October, which is the first Sunday on or after Oct 25.
        dststart_1987_2006 = datetime(1, 4, 1, 2)
        dstend_1987_2006 = datetime(1, 10, 25, 1)
        # From 1967 to 1986, DST used to start at 2am (standard time) on the last
        # Sunday in April (the one on or after April 24) and to end at 2am (DST time;
        # 1am standard time) on the last Sunday of October, which is the first Sunday
        # on or after Oct 25.
        dststart_1967_1986 = datetime(1, 4, 24, 2)
        dstend_1967_1986 = dstend_1987_2006

        if dt is None or dt.tzinfo is None:
            # An exception may be sensible here, in one or both cases.
            # It depends on how you want to treat them.  The default
            # fromutc() implementation (called by the default astimezone()
            # implementation) passes a datetime with dt.tzinfo is self.
            return zero
        assert dt.tzinfo is self

        # Find start and end times for US DST. For years before 1967, return
        # ZERO for no DST.
        if dt.year > 2006:
            dststart, dstend = dststart_2007, dstend_2007
        elif 1986 < dt.year < 2007:
            dststart, dstend = dststart_1987_2006, dstend_1987_2006
        elif 1966 < dt.year < 1987:
            dststart, dstend = dststart_1967_1986, dstend_1967_1986
        else:
            return zero

        start = self.first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = self.first_sunday_on_or_after(dstend.replace(year=dt.year))

        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        if start <= dt.replace(tzinfo=None) < end:
            return hour
        else:
            return zero
