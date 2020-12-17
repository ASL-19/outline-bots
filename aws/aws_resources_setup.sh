#!/bin/bash

options() {
  echo "------------"
  echo "Script Usage"
  echo "------------"
  echo ""
  echo "Options:"
  echo ""
  echo "-e | --email  : Setup AWS resources for email responder"
  echo "-t | --telegram : Setup AWS resources for telegram bot"
  echo ""
}

echo "---------------------------------------"
echo "AWS Setup Script"
echo "---------------------------------------"
echo ""

if [ $# -eq 0 ]
then
  options
  exit 1
else
  key="$1"
  case $key in
      -t|--telegram)
      if [[ ! -f  ../env_telegram.sh ]] ; then
          echo 'Please set up the values in env_telegram.sh file first. Aborting'
          exit
      else
          echo 'Setting up AWS Respurces ...' 
          cd telegram
          bash ./aws_setup_script.sh
      fi
      exit 0
      ;;
      -e|--email)
      if [[ ! -f  ../env_email.sh ]] ; then
          echo 'Please set up the values in env_email.sh file first. Aborting'
          exit
      else
          echo 'Setting up AWS Respurces ...' 
          cd email
          bash aws_setup_script.sh
      fi
      exit 0
      ;;
      *)
      # unknown option
      options
      exit 1
      ;;
  esac
fi
