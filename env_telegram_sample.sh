### AWS Resources
# Your AWS Account number
export AWS_ACCOUNT=
# The AWS region code you wish to use for lambda
export AWS_LAMBDA_REGION=
# The AWS region code (e.g. us-east-1) you wish to use for other new resources
export AWS_REGION=

## These are the names you wish to use for the new AWS resources and policies.
## They should not already exist.
# New user to handle Lambda install and update
export AWS_ACCESS_USER_NAME=
export AWS_DYNAMODB_TABLE=
export AWS_INFO_DYNAMODB_TABLE=
export AWS_POLICY_NAME=
export AWS_LAMBDA_ROLE=
export AWS_LAMBDA_FUNCTION=
export AWS_API_GATEWAY=
export AWS_API_GATEWAY_STAGE_NAME=

### Telegram Configuration
# When you create a new telegram bot, you get a token. Put that token here.
export TELEGRAM_TOKEN=

### Build phase env vars - these are used when you build the lambda code with
### build.sh
## API Details for outline-distribution
# The base API URL for the outline-distribution apps
# Example: API_URL=https://URL/api/v1
export API_URL=
# The Key part of the django-rest-framework Token you set up for the user.
# You need to create a user within outline-distribution and create a new
# Token for it. Do not include "Token" at the start.
export API_KEY=
# These are the numeric user IDs (not usernames) for the telegram users who
# should have access to the /admin command within the Telegram bot.
# Example: ADMIN_LIST="['$TELEGRAM_ID_OF_USER1', '$TELEGRAM_ID_OF_USER2']"
export ADMIN_LIST=

# DO NOT CHANGE:
export AWS_DYNAMO_TABLE=${AWS_DYNAMODB_TABLE}
export AWS_INFO_DYNAMO_TABLE=${AWS_INFO_DYNAMODB_TABLE}

### Install phase env vars
# DO NOT CHANGE:
export LAMBDA_FUNCTION_NAME=${AWS_LAMBDA_FUNCTION}
export LAMBDA_ROLE=${AWS_LAMBDA_ROLE}
export AWS_LAMBDA_REGION_NAME=${AWS_LAMBDA_REGION}
export AWS_ACCOUNT=${AWS_ACCOUNT}

