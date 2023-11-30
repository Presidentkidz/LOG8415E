import boto3
import logging
from auth import EC2AuthManager
import csv
import json

# boto3.set_stream_logger('', logging.DEBUG)

# Create an EC2 resource
ec2_resource = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
    
class EC2InstancesManager:
    def __init__(self):
        self.ec2_resource = boto3.resource('ec2')
        self.ec2_client = boto3.client('ec2')
        self.auth_manager = EC2AuthManager()

        self.standalone_key_pair_name: str = self.auth_manager.get_or_create_key_pair('standalone-key')
        self.gatekeeper_key_pair_name: str = self.auth_manager.get_or_create_key_pair('gatekeeper-key')
        self.trusted_host_key_pair_name: str = self.auth_manager.get_or_create_key_pair('trusted_host-key')
        self.proxy_key_pair_name: str = self.auth_manager.get_or_create_key_pair('proxy-key')
        self.manager_key_pair_name: str = self.auth_manager.get_or_create_key_pair('manager-key')
        self.worker_key_pair_name: str = self.auth_manager.get_or_create_key_pair('worker-key')

        self.standalone_security_group_id: str = self.auth_manager.get_or_create_security_group('standalone-group')
        self.gatekeeper_security_group_id: str = self.auth_manager.get_or_create_security_group('gatekeeper-group')
        self.trusted_host_security_group_id: str = self.auth_manager.get_or_create_security_group('trusted_host-group')
        self.proxy_security_group_id: str = self.auth_manager.get_or_create_security_group('proxy-group')
        self.manager_security_group_id: str = self.auth_manager.get_or_create_security_group('manager-group')
        self.worker_security_group_id: str = self.auth_manager.get_or_create_security_group('worker-group')

        self.instance_ami_id = 'ami-053b0d53c279acc90' # Ubuntu Server 22.04 LTS Ami ID
        self.availability_zone = 'us-east-1a'
        self.save = None
    
    def create_instances(self, instance_name: str, instance_type: str, key_pair_name: str, security_group_id: str, num_instances: int):
        """
        Create EC2 instances.

        :param instance_name: Name tag of the created instance 
        :param instance_type: Type of the created instance
        :param security_group_id: Security group id
        :param num_instances: Number of instances to create
        """
        volume_size = 10

        instances = self.ec2_resource.create_instances(
            ImageId=self.instance_ami_id,
            MinCount=num_instances,
            MaxCount=num_instances,
            InstanceType=instance_type,
            KeyName=key_pair_name,
            SecurityGroupIds=[security_group_id],
            Placement={
                'AvailabilityZone': self.availability_zone
            },
            TagSpecifications=[
                {
                    'ResourceType': 'instance', 
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        },
                    ]
                },
            ],
            BlockDeviceMappings=[
                {
                    "DeviceName": "/dev/sda1",
                    "Ebs": { 
                        "VolumeSize": volume_size
                    }
                }
            ]
        )

        for instance in instances:
            instance.wait_until_running()

        print("Created {} {} instances of type {} with security group {}.".format(num_instances, instance_name, instance_type, security_group_id))
    
    def _instanceToObject(self, instance):
        """
        Retrieve attributes from instance.
        Attributes are used for CSV file

        :param instance: EC2 instance to extract attributes
        """
        return {
            'name': [item['Value'] for item in instance.tags if item['Key'] == 'Name'][0],
            'user_name': 'ubuntu',
            'public_dns_name': instance.public_dns_name,
            'public_ip_address': instance.public_ip_address,
            'state': instance.state['Name']
        }

    def isInstanceRunning(self, instance):
        """
        Check if instance is running

        :param instance: EC2 instance to check status
        """
        return instance['state'] == 'running'

    def saveInstancesToCSV(self):
        """
        Save all instances to CSV file
        """
        tmp_instances = list(map(self._instanceToObject, self.ec2_resource.instances.all()))
        tmp_instances = filter(self.isInstanceRunning, tmp_instances)
        self.save = tmp_instances
        fields = ['name', 'user_name', 'public_dns_name', 'public_ip_address', 'state']
        filename = 'var/ec2_instances.csv'
        with open(filename, 'w') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames = fields) 
            writer.writeheader() 
            writer.writerows(tmp_instances)
        print("Instances saved to '{}'".format(filename))
        

if __name__ == "__main__":
    ec2_manager = EC2InstancesManager()
    
    ec2_manager.auth_manager.modify_security_group_standalone(ec2_manager.standalone_security_group_id)
    ec2_manager.auth_manager.modify_security_group_gatekeeper(ec2_manager.gatekeeper_security_group_id)
    ec2_manager.auth_manager.modify_security_group_trusted_host(ec2_manager.trusted_host_security_group_id)
    ec2_manager.auth_manager.modify_security_group_proxy(ec2_manager.proxy_security_group_id)
    ec2_manager.auth_manager.modify_security_group_manager(ec2_manager.manager_security_group_id)
    ec2_manager.auth_manager.modify_security_group_worker(ec2_manager.worker_security_group_id)

    ec2_manager.create_instances('standalone', 't2.micro', ec2_manager.standalone_key_pair_name, ec2_manager.standalone_security_group_id, 1)
    ec2_manager.create_instances('gatekeeper', 't2.large', ec2_manager.gatekeeper_key_pair_name, ec2_manager.gatekeeper_security_group_id, 1)
    ec2_manager.create_instances('trusted_host', 't2.large', ec2_manager.trusted_host_key_pair_name, ec2_manager.trusted_host_security_group_id, 1)
    ec2_manager.create_instances('proxy', 't2.large', ec2_manager.proxy_key_pair_name, ec2_manager.proxy_security_group_id, 1)
    ec2_manager.create_instances('manager', 't2.micro', ec2_manager.manager_key_pair_name, ec2_manager.manager_security_group_id, 1)
    ec2_manager.create_instances('worker', 't2.micro', ec2_manager.worker_key_pair_name, ec2_manager.worker_security_group_id, 3)

    ec2_manager.saveInstancesToCSV()