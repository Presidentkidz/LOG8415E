import csv
from fabric import Connection

class Standalone:
    def __init__(self):
        self.host, self.user_name = self._getSSHCredentials()
        self.connect_kwargs = {'key_filename': ['var/standalone-key.pem']}
        self.connection = Connection(self.host, user='ubuntu', connect_kwargs=self.connect_kwargs)

    def _getSSHCredentials(self):
        """
        Reads username and host for SSH 
        """
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            # Reconstruct instances list from file
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['name'] == 'standalone':
                    return (row['public_dns_name'], row['user_name'])
                
    def getConnection(self):
        return self.connection
    
    def deployMySQL(self):
        """
        Deploys MySQL through SSH connection
        """
        try:
            print('Starting MySQL deployment...')

            self.connection.run('sudo apt-get install mysql-server')
            self.connection.run('sudo mysql_secure_installation')

            self.connection.run('sudo mysql_secure_installation')

            mysql_commands = """
            CREATE DATABASE sakila;
            USE sakila;
            SOURCE https://downloads.mysql.com/docs/sakila-schema.sql;
            SOURCE https://downloads.mysql.com/docs/sakila-data.sql;
            SELECT * FROM sakila.actor LIMIT 10;
            EXIT;
            """
            self.connection.run(f'echo "{mysql_commands}" | mysql -u root -p root', hide=False, warn=True)




            print('MySQL deployment finished sucessfully')
        except Exception as e:
            print('Deployment Failed: ')
            print(e)

if __name__ == "__main__":
    s = Standalone()
    s.deployMySQL()