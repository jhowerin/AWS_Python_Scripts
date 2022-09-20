# Access AWS and remove an account from the Organization
# This script will remove the account with the ID you specify
# You must be the master account to run this script
# You must have the AWS CLI installed and configured
import boto3
import json
# list all AWS accounts in the Organization
orgClient = boto3.client('organizations')
response = orgClient.list_accounts()
# json dump to see the structure of the response
# comment this out when you are done analyzing the response
# print(json.dumps(response, indent=4, sort_keys=True, default=str))
for account in response['Accounts']:
    print(account['Name'], account['Id'], account['Email'], account['Status'])
# Close the account with the ID you specify
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations.html#Organizations.Client.remove_account_from_organization
# Input the account id
account_id = input("Enter the account id to remove: ")
# Close the account
response = orgClient.close_account(
    AccountId=account_id
)
# List all accounts
response = orgClient.list_accounts()
# json dump to see the structure of the response
# comment this out when you are done analyzing the response
# print(json.dumps(response, indent=4, sort_keys=True, default=str))
for account in response['Accounts']:
    print(account['Name'], account['Id'], account['Email'], account['Status'])
