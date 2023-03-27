import argparse
import subprocess

# Create an argument parser
parser = argparse.ArgumentParser(description='SSH into all AWS instances and run df -T /')

# Add arguments for the account ID, region, and profile
parser.add_argument('--account-id', required=True, help='The AWS account ID')
parser.add_argument('--region', required=True, help='The AWS region')
parser.add_argument('--profile', required=True, help='The AWS profile to use')

# Parse the command-line arguments
args = parser.parse_args()

# Use the AWS CLI to get a list of running instances in the specified account and region
cmd = f'aws ec2 describe-instances --filters "Name=instance-state-name,Values=running" --query "Reservations[].Instances[].[PublicIpAddress, InstanceId]" --output text --profile {args.profile} --region {args.region}'
output = subprocess.check_output(cmd, shell=True)

# Parse the output of the AWS CLI command to extract the IP addresses and instance IDs
instances = []
for line in output.decode().split('\n'):
    if not line:
        continue
    fields = line.strip().split('\t')
    instances.append({'ip_address': fields[0], 'instance_id': fields[1]})

# Loop over all instances and SSH into each one to run the command
for instance in instances:
    print(f'Connecting to {instance["instance_id"]} ({instance["ip_address"]})...')
    ssh_cmd = f'ssh -i ec2-get-file-system.pem ec2-user@{instance["ip_address"]} df -T /'
    subprocess.run(ssh_cmd, shell=True)
