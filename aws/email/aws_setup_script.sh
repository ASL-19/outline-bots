#!/bin/bash

source ../../env_email.sh
envsubst "$(env | cut -d= -f1 | sed -e 's/^/$/')" < ./outline_iam_policy_file_sample.json  > "./outline_iam_policy_file.json"

### Functions

create_lambda_role () {
echo "--------------------------"
echo "Creating Lambda Role      "
echo "--------------------------"
echo ""
aws iam create-role --role-name ${AWS_LAMBDA_ROLE} --assume-role-policy-document file://outline_iam_assume_role_policy.json --description "Allows Lambda functions to call AWS services on your behalf"
# Assign the policy to the role
aws iam put-role-policy --role-name ${AWS_LAMBDA_ROLE} --policy-name ${AWS_POLICY_NAME} --policy-document file://outline_iam_policy_file.json
}

create_permission_policy () {
echo "----------------------------"
echo "Creating Permission Policy  "
echo "----------------------------"
echo ""
aws iam create-policy --policy-name ${AWS_POLICY_NAME} --policy-document file://outline_iam_policy_file.json  --description "Policy for the Lambda funtion"
}

create_iam_user () {
echo "----------------------------"
echo "Creating the IAM User       "
echo "----------------------------"
echo ""
aws iam create-user --user-name ${AWS_ACCESS_USER_NAME}

TEMP_VAR=$(aws iam create-access-key --user-name ${AWS_ACCESS_USER_NAME}) 

echo $TEMP_VAR | python3 -c "import sys, json; print('export AWS_ACCESS_KEY_ID={}'.format(json.load(sys.stdin)['AccessKey']['AccessKeyId']))" >> ../../env_email.sh

echo $TEMP_VAR | python3 -c "import sys, json; print('export AWS_SECRET_ACCESS_KEY={}'.format(json.load(sys.stdin)['AccessKey']['SecretAccessKey']))" >> ../../env_email.sh

unset TEMP_VAR

# Attach the policy to the user
aws iam attach-user-policy --policy-arn arn:aws:iam::${AWS_ACCOUNT}:policy/${AWS_POLICY_NAME} --user-name ${AWS_ACCESS_USER_NAME}
}

create_lambda_function () {
echo "--------------------------"
echo "Creating Lambda Function  "
echo "--------------------------"
echo ""
aws lambda create-function \
    --region ${AWS_LAMBDA_REGION} \
    --function-name ${AWS_LAMBDA_FUNCTION} \
    --description "Outline Distribution Bot" \
    --zip-file fileb://init_lambda.zip \
    --role arn:aws:iam::${AWS_ACCOUNT}:role/${AWS_LAMBDA_ROLE} \
    --handler outlinebot.bot_handler \
    --runtime python3.8 \
    --timeout 10 \
    --memory-size 128 
}


# Create IAM permission policy:
create_permission_policy

# Create Lambda Role:
create_lambda_role
sleep 10

# Create IAM user for Lambda code deploy and update:
create_iam_user

# Create Lambda Function:
create_lambda_function


