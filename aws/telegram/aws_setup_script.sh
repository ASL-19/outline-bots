#!/bin/bash

source ../../env_telegram.sh
envsubst "$(env | cut -d= -f1 | sed -e 's/^/$/')" < ./outline_dynamodb_table_sample.json  > "./outline_dynamodb_table.json"
envsubst "$(env | cut -d= -f1 | sed -e 's/^/$/')" < ./outline_info_dynamodb_table_sample.json  > "./outline_info_dynamodb_table.json"
envsubst "$(env | cut -d= -f1 | sed -e 's/^/$/')" < ./outline_iam_policy_file_sample.json  > "./outline_iam_policy_file.json"

### Functions

create_dynamo_tables () {
echo "--------------------------"
echo "Creating DynamoDB Tables  "
echo "--------------------------"
echo ""
aws dynamodb create-table --cli-input-json file://outline_dynamodb_table.json --region ${AWS_REGION}
aws dynamodb create-table --cli-input-json file://outline_info_dynamodb_table.json --region ${AWS_REGION}
}

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

echo $TEMP_VAR | python3 -c "import sys, json; print('export AWS_ACCESS_KEY_ID={}'.format(json.load(sys.stdin)['AccessKey']['AccessKeyId']))" >> ../../env_telegram.sh

echo $TEMP_VAR | python3 -c "import sys, json; print('export AWS_SECRET_ACCESS_KEY={}'.format(json.load(sys.stdin)['AccessKey']['SecretAccessKey']))" >> ../../env_telegram.sh

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

create_api_gateway () {
echo "----------------------------"
echo "Creating API Gateway        "
echo "----------------------------"
echo ""
API_GATEWAY_ID=$(aws apigateway create-rest-api --name ${AWS_API_GATEWAY} --region ${AWS_REGION} --query 'id' --output text)

API_RESOURCE_ROOT_ID=$(aws apigateway get-resources --rest-api-id ${API_GATEWAY_ID} --region ${AWS_REGION} --query 'items[0].id' --output text) 

API_RESOURCE_ID=$(aws apigateway create-resource --rest-api-id ${API_GATEWAY_ID} --region ${AWS_REGION} --parent-id ${API_RESOURCE_ROOT_ID} --path-part telegram --query 'id' --output text)

aws apigateway put-method --rest-api-id ${API_GATEWAY_ID} --resource-id ${API_RESOURCE_ID} --http-method POST --authorization-type "NONE" --region ${AWS_REGION}

aws apigateway create-model --rest-api-id ${API_GATEWAY_ID} --region ${AWS_REGION} --content-type 'application/json' --name outline --schema '{ "$schema": "http://json-schema.org/draft-04/schema#", "title" : "Empty Schema", "type" : "object" }'

aws apigateway put-method-response --region ${AWS_REGION} --rest-api-id ${API_GATEWAY_ID} --resource-id ${API_RESOURCE_ID} --http-method POST --status-code 200 --response-models '{"application/json":"outline"}'

# Integration with Lambda:
aws apigateway put-integration \
        --region ${AWS_REGION} \
        --rest-api-id ${API_GATEWAY_ID} \
        --resource-id ${API_RESOURCE_ID} \
        --content-handling CONVERT_TO_TEXT \
        --http-method POST \
        --type AWS \
        --integration-http-method POST \
        --uri arn:aws:apigateway:${AWS_LAMBDA_REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${AWS_LAMBDA_REGION}:${AWS_ACCOUNT}:function:${AWS_LAMBDA_FUNCTION}/invocations \
        --request-templates file://lambda_integration_request_template.json 

aws apigateway put-integration-response \
        --region ${AWS_REGION} \
        --rest-api-id ${API_GATEWAY_ID} \
        --resource-id ${API_RESOURCE_ID} \
        --http-method POST \
        --status-code 200 \
        --response-templates '{"application/json": ""}'
}

lambda_api_permission () {
echo "---------------------------------"
echo "Adding API permission to Lambda  "
echo "---------------------------------"
echo ""
aws lambda add-permission \
    --function-name ${AWS_LAMBDA_FUNCTION} \
    --region ${AWS_LAMBDA_REGION} \
    --action lambda:InvokeFunction \
    --statement-id apigateway \
    --principal apigateway.amazonaws.com \
    --source-arn arn:aws:execute-api:${AWS_REGION}:${AWS_ACCOUNT}:${API_GATEWAY_ID}/*/POST/telegram
}

create_api_deployment () {
echo "---------------------------------"
echo "Creating API Deployment          "
echo "---------------------------------"
echo ""
aws apigateway create-deployment --rest-api-id ${API_GATEWAY_ID} --stage-name ${AWS_API_GATEWAY_STAGE_NAME} --region ${AWS_REGION} --variables '{"lang": "en", "token": "'${TELEGRAM_TOKEN}'"}'

INVOKE_URL=https://${API_GATEWAY_ID}.execute-api.${AWS_REGION}.amazonaws.com/${AWS_API_GATEWAY_STAGE_NAME}/telegram
echo ""
echo "THIS IS THE INVOKE_URL, THE API ADDRESS TO SET AT TELEGRAM BOT SIDE:"
echo ""
echo $INVOKE_URL
}


# Create Dynamodb Tables:
create_dynamo_tables

# Create IAM permission policy:
create_permission_policy

# Create Lambda Role:
create_lambda_role
sleep 10

# Create IAM user for Lambda code deploy and update:
create_iam_user

# Create Lambda Function:
create_lambda_function

# Create API Gateway:
create_api_gateway

# Add API permission to Lambda:
lambda_api_permission

# Create API Deployment: 
create_api_deployment

