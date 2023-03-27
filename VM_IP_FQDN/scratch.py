# Jake Howering
# jhowerin@gmail.com
# Oct 2022
# Get all AWS EC2 Names, IPs and FQDNs
# Requirements to run script
# 1. AWS CLI installed and configured
# 2. Python 3.6 or higher
# 3. Boto3 installed
# 4. You must know your AWS Management Account ID
# 5. You must be able to assume role into your AWS Members Accounts from the Management Account
import boto3
import json

print("******************************************************************")
print("Welcome to the AWS Organization EC2 Name, IP and FQDN Report")
print("To get started, please enter the AWS Organization Main Account ID: ")
orgMainAccountID = input()

orgClient = boto3.client('organizations')
response = orgClient.list_accounts()
# print out the json dump to find investigate the json response
# print(json.dumps(response, indent=4, sort_keys=True, default=str))
print("*********************************")
# Print the list of accounts in the Organization
print('The Accounts in the Organization:')
for account in response['Accounts']:
    print(account['Name'] + ",", account['Id'] + ",", account['Email'])
print("*********************************")
print("All the VMs in all the Accounts in the Organization:")
# Iterate through the list of accounts in the Organization from the response above
for account in response['Accounts']:
    if account["Id"] == orgMainAccountID:
        # The ec2 client is used to get the list of all regions in the AWS account
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_regions()
        # Loop through all regions
        for region in response['Regions']:
            ec2Client = boto3.client('ec2', region_name=region['RegionName'])
            # Get all EC2 instances
            response = ec2Client.describe_instances()
            # Loop through all instances
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    # Only print running instances
                    try:
                        if instance["State"]["Name"] == "running":
                            print("Account Name:", account['Name']+",", "Region: {}, Name: {}, Private IP: {}, Public IP: {}, FQDN: {}".format(
                                region['RegionName'],
                                # get instance name from Tag Name
                                [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'][0],
                                instance["PrivateIpAddress"],
                                instance["PublicIpAddress"],
                                #instance["PrivateDnsName"]
                                instance["PublicDnsName"]
                            ))
                    except KeyError as missing_key:
                        # Used as missing_key for readability purposes only
                        print(f"Trying to access a <dict> with a missing key {missing_key}")
        print("*****")
    else:       
        # Check only "Active" accounts
        if account['Status'] == 'ACTIVE':
            # Assume role into child account
            if account["Id"] != orgMainAccountID:
                stsClient = boto3.client('sts')
                roleArn = "arn:aws:iam::" + account['Id'] + ":role/OrganizationAccountAccessRole"
                stsresponse = stsClient.assume_role(RoleArn=roleArn, RoleSessionName='newsession')
                # Save the details from assumed role into vars
                newsession_id = stsresponse["Credentials"]["AccessKeyId"]
                newsession_key = stsresponse["Credentials"]["SecretAccessKey"]
                newsession_token = stsresponse["Credentials"]["SessionToken"]
                ec2_client = boto3.client('ec2')
                response = ec2_client.describe_regions()
                # Loop through all regions
                for region in response['Regions']:
                    # Use the assumed session vars to create a new boto3 client with the assumed role creds
                    ec2Client = boto3.client('ec2', 
                        region_name=region['RegionName'],
                        aws_access_key_id=newsession_id, 
                        aws_secret_access_key=newsession_key, 
                        aws_session_token=newsession_token)
                    # Get all EC2 instances
                    response = ec2Client.describe_instances()
                    # Loop through all instances
                    for reservation in response["Reservations"]:
                        for instance in reservation["Instances"]:
                            # Only print running instances
                            # print(json.dumps(instance, indent=4, sort_keys=True, default=str))
                            try:
                                if instance["State"]["Name"] == "running":
                                    print("Account Name:",account['Name']+",", "Region: {}, Name: {}, Private IP: {}, Public IP: {}, FQDN: {}".format(
                                        region['RegionName'],
                                        # get instance name from Tag Name
                                        [tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name'][0],
                                        #instance["InstanceId"],
                                        instance["PrivateIpAddress"],
                                        instance["PublicIpAddress"],
                                        #instance["PrivateDnsName"]
                                        instance["PublicDnsName"]
                                    ))
                            except KeyError as missing_key:
                                # Used as missing_key for readability purposes only
                                print(f"Trying to access a <dict> with a missing key {missing_key}") 
            print("*****")
print("******************************************************************")