import csv
import time
from fabric import Connection

class TrustedHost:
    def __init__(self):
        self.host, self.user_name = self._getSSHCredentials_Trusted_host()
        self.connect_kwargs = {'key_filename': ['var/trusted_host-key.pem']}
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
                
    def configureTrustedHost(self):
        # Transfer the needed files over
        self.connection.put('trusted_host.py', remote='/home/ubuntu')
        self.connection.put('requirements.txt', remote='/home/ubuntu')

        # Setup the flask app
        self.connection.run('sudo apt update')
        self.connection.run('sudo apt upgrade')

        self.connection.run('sudo apt install python3')
        self.connection.run('sudo apt install python3-pip')

        self.connection.run('pip install -r requirements.txt')

        proxy_dns, proxy_name = self._getSSHCredentials_Proxy()

        # Start the flask app
        self.connection.run(f'python3 trusted_host.py {proxy_dns}')



if __name__ == "__main__":
    t = TrustedHost()
    t.configureTrustedHost()
