# Get all AWS EKS resources in the AWS Organization
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks.html#EKS.Client.list_clusters
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks.html#EKS.Client.list_nodegroups
from errno import ESOCKTNOSUPPORT
import boto3
import json
# Access AWS to find all AWS accounts in the Organization
# and print out the account Name, ID, and Email owner
# You must be the master account to run this script
# You must have the AWS CLI installed and configured
orgClient = boto3.client('organizations')
response = orgClient.list_accounts()
# json dump to see the structure of the response
# comment this out when you are done analyzing the response
# print(json.dumps(response, indent=4, sort_keys=True, default=str))
# print(response)
print("Welcome to the AWS Organization EKS Cluster and Nodegroup Lister")
print("You must know the AWS Organization Main Account ID to run this script")
print("Please enter the AWS Organization Main Account ID: ")
orgMainAccountID = input()
print("*****")
for account in response['Accounts']:
    if account["Id"] == orgMainAccountID:
            print("Checking the AWS Organization Master Account for the EKS resources")
            print(account['Name'], account['Id'], account['Email'], account['Status'])
            eksClient = boto3.client('eks', 
                region_name='us-east-1')
            clusterResponse = eksClient.list_clusters()
            if clusterResponse['clusters'] == []:
                print("There are no EKS clusters")
            else:
                for cluster in clusterResponse['clusters']:
                    print("Cluster name: ",cluster)
                nodegroupResponse = eksClient.list_nodegroups(clusterName=cluster)
                for nodegroup in nodegroupResponse['nodegroups']:
                    print(nodegroup)
            print("*****")
    # Check only "Active" accounts
    if account['Status'] == 'ACTIVE':
        # Assume role into child account
        if account["Id"] != orgMainAccountID:
            print(account['Name'], account['Id'], account['Email'], account['Status'])
            stsClient = boto3.client('sts')
            roleArn = "arn:aws:iam::" + account['Id'] + ":role/OrganizationAccountAccessRole"
            stsresponse = stsClient.assume_role(RoleArn=roleArn, RoleSessionName='newsession')
            # Save the details from assumed role into vars
            newsession_id = stsresponse["Credentials"]["AccessKeyId"]
            newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
            newsession_token = stsresponse["Credentials"]["SessionToken"]
            # Use the assumed session vars to create a new boto3 client with the assumed role creds
            eksClient = boto3.client('eks', 
                region_name='us-east-1',
                aws_access_key_id=newsession_id, 
                aws_secret_access_key=newsession_key, 
                aws_session_token=newsession_token)

            clusterResponse = eksClient.list_clusters()
            # print(clusterResponse)
            if clusterResponse['clusters'] == []:
                print("There are no EKS clusters")
            else:
                for cluster in clusterResponse['clusters']:
                    print("Cluster name: ",cluster)
                nodegroupResponse = eksClient.list_nodegroups(clusterName=cluster)
                for nodegroup in nodegroupResponse['nodegroups']:
                    print(nodegroup)
            print("*****")
        


        
