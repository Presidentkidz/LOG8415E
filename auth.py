import os
import boto3

class EC2AuthManager:
    def __init__(self):
        self.ec2_client = boto3.client('ec2')

    def get_security_group_id(self, group_name):
        response = self.ec2_client.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [group_name]}
            ]
        )
        return response['SecurityGroups'][0]['GroupId']
    
    def get_or_create_key_pair(self, key_name):
        """
        Returns name of the created key.
        Save key to key_name.pem
        If private key .pem file is not found, delete old key and create new one.

        :param key_name: name of the key to fetch
        """
        key_dir = 'var/'
        key_file_path = os.path.join(key_dir, f'{key_name}.pem')
        # Check if the key pair already exists
        if (os.path.exists(key_file_path)):
            print(f'Key pair "{key_name}" already exists.')
            return key_name

        try:
            # Create key pair
            response = self.ec2_client.create_key_pair(KeyName=key_name)
            if (not os.path.exists(key_dir)):
                os.makedirs(key_dir)
            with open(key_file_path, 'w') as key_file:
                key_file.write(response['KeyMaterial'])
            print(f'Key pair "{key_name}" created and saved to "{key_file_path}".')
            return response['KeyName']
        except: # Key already exists, and .pem not available
            # Delete existing key
            print('Key already exists, cant find .pem file')
            self.ec2_client.delete_key_pair(KeyName=key_name)
            response = self.ec2_client.create_key_pair(KeyName=key_name)
            if (not os.path.exists(key_dir)):
                os.makedirs(key_dir)
            with open(key_file_path, 'w') as key_file:
                key_file.write(response['KeyMaterial'])
            print(f'Key pair "{key_name}" created and saved to "{key_file_path}".')
            return response['KeyName']


    def get_or_create_security_group(self, group_name):
        """
        Returns name of the created security group.
        If group already exists, returns existing security group name.
        Allows inbound HTTP, HTTPS, and SSH traffic.
        
        :param group_name: name of the security group to fetch
        """
        # Check if the security group already exists
        existing_group = self.ec2_client.describe_security_groups(
            Filters=[
                dict(Name='group-name', Values=[group_name])
            ]
        )

        if (len(existing_group['SecurityGroups']) > 0):
            group_id = existing_group['SecurityGroups'][0]['GroupId']
            print(f'Security group "{group_name}" already exists with ID: {group_id}')
            return existing_group['SecurityGroups'][0]['GroupId']

        print('Security Group does not exist.')
        # Create the security group
        security_group = self.ec2_client.create_security_group(
            GroupName=group_name,
            Description=f'Security group for {group_name}'
        )

        group_id = security_group['GroupId']

        print(f'Security group "{group_name}" created with ID: {group_id}')

        return group_id
        
    def modify_security_group_standalone(self, group_id):

        # Allow inbound HTTP, HTTPS, SSH and SQL traffic from anywhere
        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'HTTP access from anywhere',
                        },
                    ],
                    'ToPort': 80,
                },
            ],
        )

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 443,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'HTTPS access from anywhere',
                        },
                    ],
                    'ToPort': 443,
                },
            ],
        )
        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access from anywhere',
                        },
                    ],
                    'ToPort': 22,
                },
            ],
        )

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 3306,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SQL access from anywhere',
                        },
                    ],
                    'ToPort': 3306,
                },
            ],
        )

        # Allow outbound traffic to anywhere
        self.ec2_client.authorize_security_group_egress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',  # Allows all protocols
                    'FromPort': 0,  # For TCP/UDP, this specifies the starting range of the port
                    'ToPort': 65535,  # For TCP/UDP, this specifies the ending range of the port
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Destination for traffic: 0.0.0.0/0 represents all IP addresses
                }
            ]
        )

    def modify_security_group_gatekeeper(self, group_id):

        # Allow inbound HTTP, HTTPS, SSH and SQL traffic from anywhere
        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'HTTP access from anywhere',
                        },
                    ],
                    'ToPort': 80,
                },
            ],
        )

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 443,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'HTTPS access from anywhere',
                        },
                    ],
                    'ToPort': 443,
                },
            ],
        )
        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access from anywhere',
                        },
                    ],
                    'ToPort': 22,
                },
            ],
        )

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 3306,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SQL access from anywhere',
                        },
                    ],
                    'ToPort': 3306,
                },
            ],
        )

        # Allow outbound traffic to anywhere
        self.ec2_client.authorize_security_group_egress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',  # Allows all protocols
                    'FromPort': 0,  # For TCP/UDP, this specifies the starting range of the port
                    'ToPort': 65535,  # For TCP/UDP, this specifies the ending range of the port
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Destination for traffic: 0.0.0.0/0 represents all IP addresses
                }
            ]
        )

    def modify_security_group_trusted_host(self, group_id):

        # Allow inbound SSH traffic from anywhere
        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access from anywhere',
                        },
                    ],
                    'ToPort': 22,
                },
            ],
        )

        # Allow inbound HTTP and HTTPS traffic from gatekeeper

        gatekeeper_id = self.get_security_group_id("gatekeeper")

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'UserIdGroupPairs': [{'GroupId': gatekeeper_id}],
                    'ToPort': 80,
                },
            ],
        )

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 443,
                    'IpProtocol': 'tcp',
                    'UserIdGroupPairs': [{'GroupId': gatekeeper_id}],
                    'ToPort': 443,
                },
            ],
        )

        # Allow outbound HTTP and HTTPS traffic to proxy

        proxy_id = self.get_security_group_id("proxy")

        self.ec2_client.authorize_security_group_egress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',  
                    'FromPort': 80,  
                    'ToPort': 80,  
                    'UserIdGroupPairs': [{'GroupId': proxy_id}],
                }
            ]
        )

        self.ec2_client.authorize_security_group_egress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',  
                    'FromPort': 443,  
                    'ToPort': 443,  
                    'UserIdGroupPairs': [{'GroupId': proxy_id}],
                }
            ]
        )

    def modify_security_group_proxy(self, group_id):
        # Allow inbound SSH traffic from anywhere
        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access from anywhere',
                        },
                    ],
                    'ToPort': 22,
                },
            ],
        )

        # Allow inbound HTTP and HTTPS traffic from trusted_host

        trusted_host_id = self.get_security_group_id("trusted_host")

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'UserIdGroupPairs': [{'GroupId': trusted_host_id}],
                    'ToPort': 80,
                },
            ],
        )

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 443,
                    'IpProtocol': 'tcp',
                    'UserIdGroupPairs': [{'GroupId': trusted_host_id}],
                    'ToPort': 443,
                },
            ],
        )

        # Allow outbound traffic to anywhere
        self.ec2_client.authorize_security_group_egress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',  # Allows all protocols
                    'FromPort': 0,  # For TCP/UDP, this specifies the starting range of the port
                    'ToPort': 65535,  # For TCP/UDP, this specifies the ending range of the port
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Destination for traffic: 0.0.0.0/0 represents all IP addresses
                }
            ]
        )

    def modify_security_group_manager(self, group_id):
        # Allow inbound SSH traffic from anywhere
        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access from anywhere',
                        },
                    ],
                    'ToPort': 22,
                },
            ],
        )

        # Allow inbound HTTP and HTTPS traffic from proxy

        proxy_id = self.get_security_group_id("proxy")

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'UserIdGroupPairs': [{'GroupId': proxy_id}],
                    'ToPort': 80,
                },
            ],
        )

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 443,
                    'IpProtocol': 'tcp',
                    'UserIdGroupPairs': [{'GroupId': proxy_id}],
                    'ToPort': 443,
                },
            ],
        )

        # Allow outbound traffic to anywhere
        self.ec2_client.authorize_security_group_egress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',  # Allows all protocols
                    'FromPort': 0,  # For TCP/UDP, this specifies the starting range of the port
                    'ToPort': 65535,  # For TCP/UDP, this specifies the ending range of the port
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Destination for traffic: 0.0.0.0/0 represents all IP addresses
                }
            ]
        )

    def modify_security_group_worker(self, group_id):
        # Allow inbound SSH traffic from anywhere
        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access from anywhere',
                        },
                    ],
                    'ToPort': 22,
                },
            ],
        )

        # Allow inbound HTTP and HTTPS traffic from manager and proxy

        manager_host_id = self.get_security_group_id("manager")
        proxy_host_id = self.get_security_group_id("proxy")

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 80,
                    'IpProtocol': 'tcp',
                    'UserIdGroupPairs': [{'GroupId': manager_host_id},
                    {'GroupId': proxy_host_id}],
                    'ToPort': 80,
                },
            ],
        )

        self.ec2_client.authorize_security_group_ingress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'FromPort': 443,
                    'IpProtocol': 'tcp',
                    'UserIdGroupPairs': [{'GroupId': manager_host_id},
                    {'GroupId': proxy_host_id}],
                    'ToPort': 443,
                },
            ],
        )

        # Allow outbound traffic to anywhere
        self.ec2_client.authorize_security_group_egress(
            GroupId=group_id,
            IpPermissions=[
                {
                    'IpProtocol': '-1',  # Allows all protocols
                    'FromPort': 0,  # For TCP/UDP, this specifies the starting range of the port
                    'ToPort': 65535,  # For TCP/UDP, this specifies the ending range of the port
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Destination for traffic: 0.0.0.0/0 represents all IP addresses
                }
            ]
        )
