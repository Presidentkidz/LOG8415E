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

    def deployMySQL(self):
        """
        Deploys MySQL through SSH connection
        """
        try:
            print('Starting MySQL deployment...')

            # Install the expect library
            self.connection.run('sudo apt-get install expect')

            # Install MySQL server
            self.connection.run('sudo apt-get install mysql-server')

            # Harden MySQL Server
            self.connection.run('spawn sudo mysql_secure_installation')

            # Answer no to install VALIDATE PASSWORD COMPONENT
            self.connection.run('expect "*:*"')
            self.connection.run('send "n\r"')

            # Answer yes to remove anonymous users
            self.connection.run('expect "*:*"')
            self.connection.run('send "y\r"')

            # Answer yes to disable root login remotely
            self.connection.run('expect "*:*"')
            self.connection.run('send "y\r"')

            # Answer yes to remove test database
            self.connection.run('expect "*:*"')
            self.connection.run('send "y\r"')

            # Answer yes to reload privilege tables
            self.connection.run('expect "*:*"')
            self.connection.run('send "y\r"')

            # Login to MySQL
            self.connection.run('mysql')

            # Download Sakila database 
            self.connection.run('wget https://downloads.mysql.com/docs/sakila-db.tar.gz -O sakila-db.tar.gz')
            self.connection.run('tar -xzvf sakila-db.tar.gz')
            self.connection.run('cd sakila-db')

            mysql_commands = """
            CREATE DATABASE sakila;
            USE sakila;
            SOURCE sakila-schema.sql;
            SOURCE sakila-data.sql;
            SELECT * FROM sakila.actor LIMIT 10;
            EXIT;
            """
            self.connection.run(f'echo "{mysql_commands}" | mysql -u root -p root', hide=False, warn=True)


            print('Standalone MySQL deployment finished sucessfully')
        except Exception as e:
            print('Deployment Failed: ')
            print(e)

if __name__ == "__main__":
    s = Standalone()
    s.deployMySQL()