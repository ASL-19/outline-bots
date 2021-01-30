# OutlineBot

## Prerequisites
- **Common between Telegram Bot and Email Responder:**
   - You should have a user in the cloud provider with enough permission to create required resources
    - A user and password created in Outline Distribution Server (API Key/token)
    - Unix-based system
    - Binary (command) envsubst is needed. Install the related package. Example for Ubuntu:
        - apt-get update
        - apt-get install gettext-base
    - Required resources in the cloud:
        - Script `aws/aws_resources_setup.sh` in repo is provided as an example. It can be used to set up the resources in Amazon Cloud
        - Resources:
            - Role or permissions needed for the serverless function to run
            - Serverless function
- **Telegram Bot:**
    - Create the Telegram Bot at Telegram side (Required for Telegram Bot)
    - Required extra resources in the cloud:
        - Rest API which Telegram API will connect to
        - Two database tables
- **Email Responder:**
    - An email address where the user sends an email to get an Outline server (eg. get@yourdomain.com). This email address will invoke the serverless function.
    - For AWS users: A verified domain in AWS SES as explained [here](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/receiving-email-setting-up.html)

## Steps
- **Steps at a glance**
    - Set up environment variables
    - Set up cloud resources (manually or using `aws_resources_setup.sh` script for AWS cloud)
    - Build:
        - NOTE: You need to do this step after any change in the code or environmental variables used in the Build stage
    - Install
        - NOTE: You need to do this step after any change in the code or environmental variables used in the Build or Install stages


    Details of each step is providev below.


- **Preparation**
    - Clone the repo
    - Go to the repo directory
    - Run these:
        - To set up Telegram Bot:
            - `cp env_telegram_sample.sh env_telegram.sh`
            - Set up the values in file `env_telegram.sh`:
            - NOTE: Use existing cloud resources information if you already have them
        - To set up Email Responder:
            - `cp env_email_sample.sh env_email.sh`
            - Set up the values in file `env_email.sh`
            - NOTE: Use existing cloud resources information if you already have them



- **Resources setup**
    - Set up required resources on AWS cloud if they don’t exist. Skip this step if you use another cloud provider or if you want to set up the resources manually:
        - Prerequisites:
            - You need to [install](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) _aws cli_
            - Create a user with Programmatic Access with enough permissions to create and change resources. You need to [configure](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) aws cli to use this user to run the script
        - Go to repo directory
            - Run these command if you haven’t done already:
                - To set up AWS resources for Telegram Bot:
                    - `cp env_telegram_sample.sh env_telegram.sh`
                    - Set up the values in file `env_telegram.sh`
                - To set up AWS resources for Email Responder:
                    - `cp env_email_sample.sh env_email.sh`
                    - Set up the values in file `env_email.sh`
            Run these commands:
                - `cd aws`
                - For Telegram Bot:
                    - `bash ./aws_resources_setup.sh -t`
                    - Make a note of the INVOKE_URL printed by script at time of completion. Set this URL as the `webhook` of the telegram bot. You can do it via [Telegram API](https://core.telegram.org/bots/api#setwebhook).
                - For Email Responder:
                    - `bash ./aws_resources_setup.sh -e`
                    -  Create a SES receipt rule with action to invoke the newly created lambda function as explained [here](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/receiving-email-receipt-rules.html). This rule should be setup with the email mentioned in Prerequisites section.
                    - NOTE: You cannot set up Email Responder if your SES is in Sandbox. Check [here](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html) to get more information and how to move out of Sandbox.
                - NOTE: Running this script will add new exports to the end of `env_telegram.sh` setting access to that of the new user. If you need to start over, be sure to remove those exports, otherwise the script will attempt to use the new user to create resources, which will fail.



 - **Build**
    - Go to repo directory
    - Run these commands:
        - For Telegram Bot:
            `bash ./build.sh -t`
        - For Email Responder:
            `bash ./build.sh -e`



- **Install**
    - Go to repo directory
    - Run these commands:
        - For Telegram Bot:
            `bash ./install.sh -t`
        - For Email Responder:
            `bash ./install.sh -e`











