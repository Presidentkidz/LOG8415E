import csv
import time
from fabric import Connection

class Proxy:
    def __init__(self):
        self.host, self.user_name = self._getSSHCredentials_Proxy()
        self.connect_kwargs = {'key_filename': ['var/proxy-key.pem']}
        self.connection = Connection(self.host, user='ubuntu', connect_kwargs=self.connect_kwargs)

    def _getSSHCredentials_Proxy(self):
        """
        Reads username and host for SSH 
        """
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            # Reconstruct instances list from file
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['name'] == 'proxy':
                    return (row['public_dns_name'], row['user_name'])
                
    def _getSSHCredentials_Manager(self):
        """
        Reads username and host for SSH 
        """
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            # Reconstruct instances list from file
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['name'] == 'manager':
                    return (row['public_dns_name'], row['user_name'])
    
    def _getSSHCredentials_Workers(self):
        """
        Reads username and host for SSH 
        """
        worker_credentials = []

        with open('var/ec2_instances.csv', mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['name'] == 'worker':
                    worker_credentials.append((row['public_dns_name'], row['user_name']))

        return worker_credentials
                
    def configureProxy(self):
        # Transfer the needed files over
        self.connection.put('proxy.py', remote='/home/ubuntu')
        self.connection.put('requirements.txt', remote='/home/ubuntu')

        # Setup the flask app
        self.connection.run('sudo apt update')
        self.connection.run('sudo apt upgrade')

        self.connection.run('sudo apt install python3')
        self.connection.run('sudo apt install python3-pip')

        self.connection.run('pip install -r requirements.txt')

        manager_dns, manager_name = self._getSSHCredentials_Manager()

        worker_credentials = self._getSSHCredentials_Workers()

        worker1_dns = worker_credentials[0].public_dns_name
        worker2_dns = worker_credentials[1].public_dns_name
        worker3_dns = worker_credentials[2].public_dns_name

        # Start the flask app
        self.connection.run(f'python3 proxy.py {manager_dns} {worker1_dns} {worker2_dns} {worker3_dns}')



if __name__ == "__main__":
    p = Proxy()
    p.configureProxy()
