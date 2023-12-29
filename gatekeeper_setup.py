import csv
import time
from fabric import Connection

class Gatekeeper:
    def __init__(self):
        self.host, self.user_name = self._getSSHCredentials_Gatekeeper()
        self.connect_kwargs = {'key_filename': ['var/gatekeeper-key.pem']}
        self.connection = Connection(self.host, user='ubuntu', connect_kwargs=self.connect_kwargs)

    def _getSSHCredentials_Gatekeeper(self):
        """
        Reads username and host for SSH 
        """
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            # Reconstruct instances list from file
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['name'] == 'gatekeeper':
                    return (row['public_dns_name'], row['user_name'])
                
    def _getSSHCredentials_Trusted_host(self):
        """
        Reads username and host for SSH 
        """
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            # Reconstruct instances list from file
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['name'] == 'trusted_host':
                    return (row['public_dns_name'], row['user_name'])
                
    def configureGatekeeper(self):
        # Transfer the needed files over
        self.connection.put('gatekeeper.py', remote='/home/ubuntu')
        self.connection.put('requirements.txt', remote='/home/ubuntu')

        # Setup the flask app
        self.connection.run('sudo apt update')
        self.connection.run('sudo apt upgrade')

        self.connection.run('sudo apt install python3')
        self.connection.run('sudo apt install python3-pip')

        self.connection.run('pip install -r requirements.txt')

        trusted_host_dns, trusted_host_name = self._getSSHCredentials_Trusted_host()

        # Start the flask app
        self.connection.run(f'python3 gatekeeper.py {trusted_host_dns}')



if __name__ == "__main__":
    g = Gatekeeper()
    g.configureGatekeeper()
