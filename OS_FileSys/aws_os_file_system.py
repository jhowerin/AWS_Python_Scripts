import argparse
import boto3
import json
import sys

# Define functions

def get_account_id(profile):
    session = boto3.Session(profile_name=profile)
    sts = session.client('sts')
    caller_identity = sts.get_caller_identity()
    if 'Account' not in caller_identity:
        print('Error: Could not retrieve AWS account ID')
        sys.exit(1)
    else:
        return caller_identity['Account']

def get_ec2_instances(account_id, region, profile):
    session = boto3.Session(profile_name=profile)
    ec2 = session.client('ec2', region_name=region)
    response = ec2.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)
    return instances

def get_operating_system(instance):
    platform = instance.get('Platform')
    if platform == 'windows':
        return 'Windows'
    else:
        return 'Linux/UNIX'

def get_platform_details(instance):
    platform = instance.get('Platform')
    if platform == 'windows':
        return instance.get('PlatformDetails')
    else:
        return None

def get_ami_name(instance):
    return instance.get('ImageId')

def get_file_systems(instance, ec2):
    block_device_mappings = instance['BlockDeviceMappings']
    file_systems = []
    for block_device_mapping in block_device_mappings:
        device_name = block_device_mapping['DeviceName']
        volume_id = block_device_mapping['Ebs']['VolumeId']
        response = ec2.describe_volumes(VolumeIds=[volume_id])
        file_system_type = response['Volumes'][0]['VolumeType']
        file_system_size = response['Volumes'][0]['Size']
        file_systems.append((device_name, file_system_type, file_system_size))
    return file_systems

def print_instance_info(account_id, region, instance, ec2):
    instance_id = instance['InstanceId']
    operating_system = get_operating_system(instance)
    platform_details = get_platform_details(instance)
    ami_name = get_ami_name(instance)
    file_systems = get_file_systems(instance, ec2)
    print(f"AWS Account: {account_id} (Region: {region})")
    print(f"Instance ID: {instance_id}")
    print(f"Operating System: {operating_system}")
    if platform_details:
        print(f"Platform Details: {platform_details}")
    print(f"AMI Name: {ami_name}")
    for device_name, file_system_type, file_system_size in file_systems:
        print(f"File System ({device_name}): {file_system_type} ({file_system_size} GB)")
    print()


# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--account-id', type=str, required=True,
                    help='The ID of the AWS account to retrieve information from')
parser.add_argument('--region', type=str, required=True,
                    help='The name of the region to retrieve information from')
parser.add_argument('--profile', type=str, help='The name of the profile to use from your AWS credentials file')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')

args = parser.parse_args()

# Retrieve AWS account ID from the command line arguments or profile
# Retrieve AWS account ID from the command line arguments or profile
account_id = args.account_id
if args.profile:
    account_id = get_account_id(args.profile)
if account_id != args.account_id:
    print(f'Using AWS account ID {account_id} from profile')

# Print AWS account ID and region
print(f"\nRetrieving information for AWS account {account_id} (Region: {args.region})\n")

# Create EC2 client
session = boto3.Session(profile_name=args.profile)
ec2 = session.client('ec2', region_name=args.region)

# Retrieve information about all EC2 instances in the region
instances = get_ec2_instances(account_id, args.region, args.profile)

# Loop through each instance in the response and print instance information
for instance in instances:
    print_instance_info(account_id, args.region, instance, ec2)

