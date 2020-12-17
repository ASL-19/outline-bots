### AWS Resources
export AWS_ACCOUNT=
export AWS_REGION=
export AWS_LAMBDA_REGION=
## New AWS Resources
# New user to handle Lambda install and update
export AWS_ACCESS_USER_NAME=
export AWS_DYNAMODB_TABLE=
export AWS_INFO_DYNAMODB_TABLE=
export AWS_POLICY_NAME=
export AWS_LAMBDA_ROLE=
export AWS_LAMBDA_FUNCTION=
export AWS_API_GATEWAY=
export AWS_API_GATEWAY_STAGE_NAME=
# From Telegram Bot:
export TELEGRAM_TOKEN=

### Build phase env vars
# Example: API_URL=https://URL/api/v1
export API_URL=
export API_KEY=
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

