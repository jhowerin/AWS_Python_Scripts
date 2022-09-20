# Access AWS to find all AWS accounts in the Organization
# and print out the account Name, ID, and Email owner
# You must be the master account to run this script
# You must have the AWS CLI installed and configured
import boto3
import json
orgClient = boto3.client('organizations')
response = orgClient.list_accounts()
# json dump to see the structure of the response
# comment this out when you are done analyzing the response
print(json.dumps(response, indent=4, sort_keys=True, default=str))
#print(response)
for account in response['Accounts']:
    print(account['Name'], account['Id'], account['Email'], account['Status'])
    