# Get all AWS EKS clusters and nodegroups from all regions in the AWS Organization
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks.html
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks.html#EKS.Client.list_clusters
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/eks.html#EKS.Client.list_nodegroups
#from errno import ESOCKTNOSUPPORT
import boto3
import json
# You must be the master account to run this script
# You must have the AWS CLI installed and configured
# These two lines get the list of all accounts in the Organization
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
            # Access EKS resources in all regions
            # The ec2 client is used to get the list of all regions
            ec2_client = boto3.client('ec2')
            response = ec2_client.describe_regions()
            # Loop through all regions
            for region in response['Regions']:
                eksClient = boto3.client('eks', region_name=region['RegionName'])
                print("AWS Main Account with region",region['RegionName'])
                clusterResponse = eksClient.list_clusters()
                if clusterResponse['clusters'] == []:
                    print("There are no EKS clusters")
                else:
                    for cluster in clusterResponse['clusters']:
                        print("Cluster name: ",cluster)
                        nodegroupResponse = eksClient.list_nodegroups(clusterName=cluster)
                    for nodegroup in nodegroupResponse['nodegroups']:
                        print("Nodegroup: ",nodegroup)
                print("*****")
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
            ec2_client = boto3.client('ec2')
            response = ec2_client.describe_regions()
            for region in response['Regions']:
                # Use the assumed session vars to create a new boto3 client with the assumed role creds
                eksClient = boto3.client('eks', 
                    region_name=region['RegionName'],
                    aws_access_key_id=newsession_id, 
                    aws_secret_access_key=newsession_key, 
                    aws_session_token=newsession_token)
                print("AWS Sub Account", account['Name'], "with region",region['RegionName'])
                clusterResponse = eksClient.list_clusters()
                if clusterResponse['clusters'] == []:
                    print("There are no EKS clusters")
                else:
                    for cluster in clusterResponse['clusters']:
                        print("Cluster name: ",cluster)
                        nodegroupResponse = eksClient.list_nodegroups(clusterName=cluster)
                    for nodegroup in nodegroupResponse['nodegroups']:
                        print("Nodegroup: ",nodegroup)
                print("*****")
        


        
