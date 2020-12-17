#!/bin/bash
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

# Project config
PROJECT_ROOT=`pwd`
DIST_DIR_NAME="dist"
DEPLOY_DIR_NAME="deploy"
LAMBDA_CODE_FILE=lambda.zip

# AWS Config
LAMBDA_FUNCTION_NAME=${LAMBDA_FUNCTION_NAME}
AWS_LAMBDA_REGION_NAME=${AWS_LAMBDA_REGION_NAME}
AWS_ACCOUNT=${AWS_ACCOUNT}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
LAMBDA_ROLE=${LAMBDA_ROLE}
LAMBDA_TIMEOUT=120
LAMBDA_MEMORY=512
## Python version
RUNTIME=python3.8

update_env_variables() {
  # update function
  echo "----------------------------"
  echo "Update Environment Variables"
  echo "----------------------------"
  echo "Lambda role:"
  echo ${LAMBDA_ROLE}
  AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  aws lambda update-function-configuration \
    --region ${AWS_LAMBDA_REGION_NAME} \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --handler ${LAMBDA_HANDLER} \
    --description "${LAMBDA_DESCRIPTION}" \
    --role arn:aws:iam::${AWS_ACCOUNT}:role/${LAMBDA_ROLE} \
    --runtime ${RUNTIME} \
    --timeout ${LAMBDA_TIMEOUT} \
    --memory-size ${LAMBDA_MEMORY} \
    --environment '{"Variables": {"DEBUG": "False"}}'
}


update_lambda() {
  # update function
  echo "-----------------------------"
  echo "Update Lambda function on AWS"
  echo "-----------------------------"
  echo ""
  AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
  AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  aws lambda update-function-code \
    --region ${AWS_LAMBDA_REGION_NAME} \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --zip-file fileb://${PROJECT_ROOT}/${DEPLOY_DIR_NAME}/${LAMBDA_CODE_FILE}
}

deploy() {
  echo "-----------------------"
  echo "Deploying to AWS Lambda"
  echo "-----------------------"
  echo ""

  # if function already exists
  if aws lambda get-function \
      --region ${AWS_LAMBDA_REGION_NAME} \
      --function-name ${LAMBDA_FUNCTION_NAME} > /dev/null; then
    update_lambda
    update_env_variables
  else
    echo "Error: The serverless function does not exist in this region."
  fi
}


options() {
  echo "------------"
  echo "Script Usage"
  echo "------------"
  echo ""
  echo "Options:"
  echo ""
  echo "-e | --email  : Install email responder code"
  echo "-t | --telegram : Install telegram bot code"
  echo ""
}


if [ $# -eq 0 ]
then
  options
  exit 1
else
  key="$1"
  case $key in
      -t|--telegram)
      source ./env_telegram.sh
      LAMBDA_DESCRIPTION="Outline Distribution Bot"
      LAMBDA_HANDLER=outlinebot.bot_handler
      deploy
      exit 0
      ;;
      -e|--email)
      source ./env_email.sh
      LAMBDA_DESCRIPTION="Outline Email Responder"
      LAMBDA_HANDLER=responder.mail_responder
      deploy
      exit 0
      ;;
      *)
      # unknown option
      options
      exit 1
      ;;
  esac
fi
