import boto3
import json

def get_account_info(account_id):
    org_client = boto3.client('organizations')
    response = org_client.list_accounts()
    accounts = {}
    for account in response['Accounts']:
        accounts[account['Id']] = account['Name']
    return accounts[account_id]

def get_account_vms(account_id, main_account_id):
    if account_id == main_account_id:
        # The ec2 client is used to get the list of all regions in the AWS account
        ec2_client = boto3.client('ec2')
        response = ec2_client.describe_regions()
        # Loop through all regions
        for region in response['Regions']:
            ec2_client = boto3.client('ec2', region_name=region['RegionName'])
            # Get all EC2 instances
            response = ec2_client.describe_instances()
            # Loop through all instances
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    # Only print running instances
                    try:
                        if instance["State"]["Name"] == "running":
                            print("Account Name:", get_account_info(account_id)+",", "Region: {}, Name: {}, Private IP: {}, Public IP: {}, FQDN: {}".format(
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
            if account_id != main_account_id:
                sts_client = boto3.client('sts')
                role_arn = "arn:aws:iam::" + account_id + ":role/OrganizationAccountAccessRole"
                sts_response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName='newsession')
                # Save the details from assumed role into vars
                newsession_id = sts_response["Credentials"]["AccessKeyId"]
                newsession_key = sts_response["Credentials"]["SecretAccessKey"]
                newsession_token = sts_response["Credentials"]["SessionToken"]
                ec2_client = boto3.client('ec2')
                response = ec2_client.describe_regions()
                # Loop through all regions
                for region in response['Regions']:
                    # Use the assumed session vars to create a new boto3 client with the assumed role
                    ec2_client = boto3.client('ec2',
                    region_name=region['RegionName'],
                    aws_access_key_id=newsession_id,
                    aws_secret_access_key=newsession_key,
                    aws_session_token=newsession_token)
                    # Get all EC2 instances
                    response = ec2_client.describe_instances()
                    # Loop through all instances
                    for reservation in response["Reservations"]:
                        for instance in reservation["Instances"]:
                        # Only print running instances
                            try:
                                if instance["State"]["Name"] == "running":
                                    print("Account Name:", get_account_info(account_id)+",", "Region: {}, Name: {}, Private IP: {}, Public IP: {}, FQDN: {}".format(
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

def main():
    print("******************************************************************")
    print("Welcome to the AWS Organization EC2 Name, IP and FQDN Report")
    print("To get started, please enter the AWS Organization Main Account ID: ")
    main_account_id = input()
    org_client = boto3.client('organizations')
    response = org_client.list_accounts()
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
        get_account_vms(account['Id'], main_account_id)

if __name__ == "__main__":
    print("hello")
    main()