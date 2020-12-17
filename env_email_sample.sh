### AWS Resources
export AWS_ACCOUNT=
export AWS_REGION=
export AWS_LAMBDA_REGION=
## New AWS Resources
# New user to handle Lambda install and update
export AWS_ACCESS_USER_NAME=
export AWS_POLICY_NAME=
export AWS_LAMBDA_ROLE=
export AWS_LAMBDA_FUNCTION=

### Build phase env vars
# Example: API_URL=https://URL/api/v1
export API_URL=
export API_KEY=
# Example: EMAIL_DOMAIN=mydomain.com
export EMAIL_DOMAIN=

### Install phase env vars
# DO NOT CHANGE:
export LAMBDA_FUNCTION_NAME=${AWS_LAMBDA_FUNCTION}
export LAMBDA_ROLE=${AWS_LAMBDA_ROLE}
export AWS_LAMBDA_REGION_NAME=${AWS_LAMBDA_REGION}
export AWS_ACCOUNT=${AWS_ACCOUNT}

