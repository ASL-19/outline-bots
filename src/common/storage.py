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
Storage Module
Holds functions for working with paskoocheh apps on S3
"""
import json
import re
from datetime import datetime
import requests
import boto3
from boto3.session import Session
from botocore.client import Config
from botocore.exceptions import ClientError
from errors import AWSError, ValidationError

S3_AMAZON_LINK = "https://s3.amazonaws.com"

def build_key_name(app_name, os_name, file_name):
    """ 
    Creates key using app name, os and filename

    :param app_name: app name
    :param os_name: OS the app is written for
    :param filename: the name of the file
    :return: S3 bucket key for given app/os/filename combination
    """
    return (app_name.replace(" ", "").lower() + "/" +
            os_name.replace(" ", "").lower() + "/" + file_name)

def build_static_link(bucket, key):
    """ 
    Creates a link based on app name os and filename

    :param key: s3 key for the resource
    :return: string url for amazon S3 file
    """
    return "https://s3.amazonaws.com/" + bucket + "/" + key

def get_binary_contents(bucket, key, config=None):
    """ 
    Get file contents from S3

    :param bucket: name of bucket
    :param key: key id in bucket
    :return: Stream object with contents
    :raise: AWSError: couldn't fetch file contents from S3
    """
    s3_resource = boto3.resource("s3") if config is None else boto3.resource("s3", config=config)
    try:
        response = s3_resource.Object(bucket, key).get()
    except ClientError as error:
        raise AWSError("Error loading file from S3: {}".format(str(error)))
    return response

def put_file_with_creds(bucket, key, content, access_key, secret_key):
    """ 
    Get a file from S3 using Specific Credentials

    :param bucket: name of bucket
    :param key: key id in bucket
    :param content: file body content
    :param access_key: user's access_key
    :param secret_key: user's secret_key
    :raise: AWSError: couldn't fetch file contents from S3
    """
    if key is None or len(key) <= 0:
        raise ValidationError("Key name cannot be empty.")

    if bucket is None or len(bucket) <= 0:
        raise ValidationError("Bucket name cannot be empty.")

    s3 = boto3.client("s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)

    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=content)

    except ClientError as error:
        raise AWSError("Problem putting {} from {} bucket ({})"
                       .format(key, bucket, str(error)))
    return

def get_file_with_creds(bucket, key, access_key, secret_key):
    """
    Get a file from S3 using Specific Credentials

    :param bucket: name of bucket
    :param key: key id in bucket
    :param access_key: user's access_key
    :param secret_key: user's secret_key
    :return: Stream object with contents
    :raise: AWSError: couldn't fetch file contents from S3
    """
    if key is None or len(key) <= 0:
        raise ValidationError("Key name cannot be empty.")

    if bucket is None or len(bucket) <= 0:
        raise ValidationError("Bucket name cannot be empty.")

    s3 = boto3.client("s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key)
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
    except ClientError as error:
        raise AWSError("Error loading file from S3: {}".format(str(error)))
    return response

def get_json_contents(bucket, key):
    """
    Get json file from S3

    :param bucket: name of bucket
    :param key: key id in bucket
    :return: JSON from S3 bucket
    :raise: AWSError: couldn't fetch file contents from S3
    """
    s3_resource = boto3.resource("s3")
    try:
        response = s3_resource.Object(bucket, key).get()
    except ClientError as error:
        raise AWSError("Error loading file from S3: {}".format(str(error)))
    return json.load(response["Body"])

def get_object_metadata(bucket, key):
    """
    Get file metadata from S3

    :param bucket: name of bucket
    :param key: key id in bucket
    :return: S3 metadata object
    :raise: AWSError: couldn't load metadata from S3
    """
    # Get downloads file metadata from S3 bucket
    s3_resource = boto3.resource("s3")
    obj = s3_resource.Object(bucket, key)
    try:
        obj.load()
    except ClientError as error:
        raise AWSError("Error loading metadata from S3: {}".format(str(error)))
    return obj

def put_object_metadata(bucket, key, meta_key, meta_value):
    """
    Get file metadata from S3

    :param bucket: name of bucket
    :param key: key id in bucket
    :param meta_key: key for updated metadata
    :param meta_value: value for updated metadata
    :return: S3 metadata object
    :raise: AWSError: couldn't load metadata from S3
    """
    # Get downloads file metadata from S3 bucket
    s3_client = boto3.client("s3")

    try:
        metadata = s3_client.head_object(Bucket=bucket,
                                         Key=key)["Metadata"]
        metadata[meta_key] = meta_value
        s3_client.copy_object(
            Bucket=bucket,
            Key=key,
            CopySource={
                'Bucket': bucket,
                'Key': key,
            },
            Metadata=metadata,
            MetadataDirective='REPLACE'
        )
    except ClientError as error:
        raise AWSError("Error loading metadata from S3: {}".format(str(error)))

def get_temp_link(bucket, key, key_id, secret_key, expiry=300):
    """
    Get expiring S3 url with temp token
    NB: bucket must be in us-east-1 to use path addressing!

    :param bucket: name of bucket
    :param key: key id in bucket
    :param key_id: Amazon AWS API key id
    :param secret_key: Amazon AWS Secret API key
    :param expiry: number of seconds token is valid for (default=600)
    :return: Temporary S3 link to file using temp credentials
    :raise: AWSError: error getting presigned link from S3
    """
    session = Session(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key
    )
    s3_client = session.client("s3", config=Config(s3={'addressing_style': 'path'}))
    try:
        link = s3_client.generate_presigned_url(
            ExpiresIn=expiry,
            ClientMethod="get_object",
            Params={
                "Bucket": bucket,
                "Key": key,
            }
        )
    except ClientError as error:
        raise AWSError("Error generating temp link: {}".format(str(error)))
    return link

def put_doc_file(bucket, key, filename, url, caption=None, thumb=None):
    """
    Appends to a file in S3

    :param bucket: file bucket name
    :param key: key prefix
    :param filename: filename to be written
    :param url: location of filename
    :param caption: caption file contents
    :param thumb: thumbnail file contents
    :raise: AWSError: Error adding file to S3 bucket
    """
    if key is None or len(key) <= 0:
        raise ValidationError("Key name cannot be empty.")

    s3_resource = boto3.resource("s3")

    timestr = datetime.now().strftime("%Y%m%d-%H:%M:%S.%f-")
    docobj = s3_resource.Object(bucket, key + "/" + timestr + filename)

    if caption is not None:
        capobj = s3_resource.Object(bucket, key + "/" + timestr + filename + ".cap")
    else:
        pass

    if thumb is not None:
        thumbobj = s3_resource.Object(bucket, key + "/" + timestr + filename)

    try:
        file_content = requests.get(url).content
        docobj.put(Body=file_content)
        if caption is not None:
            capobj.put(Body=caption)
        if thumb is not None:
            thumbobj.put(Body=str(thumb))

    except ClientError as error:
        raise AWSError("Problem getting {} from {} bucket ({})"
                       .format(key, bucket, str(error)))
    return

def put_text_file(bucket, key, text):
    """ 
    Appends to a file in S3

    :param bucket: file bucket name
    :param key: file key name
    :param text: text to be written
    :raise: AWSError: Error adding file to S3 bucket
    """
    if key is None or len(key) <= 0:
        raise ValidationError("Key name cannot be empty.")

    s3_resource = boto3.resource("s3")

    timestr = datetime.now().strftime("%Y%m%d-%H:%M:%S.%f.msg")
    key = key + "/" + timestr
    s3_new_file = s3_resource.Object(bucket, key)

    try:
        s3_new_file.put(Body=text)
    except ClientError as error:
        raise AWSError("Problem getting object {} from {} ({})"
                       .format(key, bucket, str(error)))
    return

def add_to_mailing_list(user_email):
    """
    Adds user to mailing list

    :param user_email: unique email of user
    :raise: ValidationError: user_email is invalid
    """
    if (user_email is None or len(user_email) <= 0
            or not re.match(r"[^@]+@[^@]+\.[^@]+", user_email)):
        raise ValidationError("User email is invalid: {}".format(user_email))
    return

