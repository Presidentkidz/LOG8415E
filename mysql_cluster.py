import csv
import time
from fabric import Connection

class Cluster:
    def __init__(self):
        self.host_manager, self.user_name_manager = self._getSSHCredentials_Manager()
        self.workers_credentials = self._getSSHCredentials_Workers()
        self.connect_kwargs_manager = {'key_filename': ['var/manager-key.pem']}
        self.connect_kwargs_worker = {'key_filename': ['var/worker-key.pem']}
        self.connection_manager = Connection(self.host_manager, user='ubuntu', connect_kwargs=self.connect_kwargs_manager)
        self.connection_worker1 = Connection(self.workers_credentials[0].public_dns_name, user='ubuntu', connect_kwargs=self.connect_kwargs_worker)
        self.connection_worker2 = Connection(self.workers_credentials[1].public_dns_name, user='ubuntu', connect_kwargs=self.connect_kwargs_worker)
        self.connection_worker3 = Connection(self.workers_credentials[2].public_dns_name, user='ubuntu', connect_kwargs=self.connect_kwargs_worker)

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
                
    
    def deployManagerNode(self):
        """
        Deploys MySQL Manager through SSH connection
        """
        try:
            print('Starting MySQL Manager deployment...')

            # Uninstall any existing Mysql packages
            self.connection_manager.run('service mysqld stop')
            self.connection_manager.run('yum remove mysql-server mysql mysql-devel')

            # Download and Extract MySQL Cluster Binaries
            self.connection_manager.run('mkdir -p /opt/mysqlcluster/home')
            self.connection_manager.run('cd /opt/mysqlcluster/home')
            self.connection_manager.run('wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz')

            # Setup Executable Path Globally
            self.connection_manager.run('echo ‘export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc’ > /etc/profile.d/mysqlc.sh')
            self.connection_manager.run('echo ‘export PATH=$MYSQLC_HOME/bin:$PATH’ >> /etc/profile.d/mysqlc.sh')
            self.connection_manager.run('source /etc/profile.d/mysqlc.sh')
            self.connection_manager.run('sudo apt-get update && sudo apt-get -y install libncurses5')

            # Create the Deployment Directory and Setup Config Files
            self.connection_manager.run('mkdir -p /opt/mysqlcluster/deploy')
            self.connection_manager.run('cd /opt/mysqlcluster/deploy')
            self.connection_manager.run('mkdir conf')
            self.connection_manager.run('mkdir mysqld_data')
            self.connection_manager.run('mkdir ndb_data')
            self.connection_manager.run('cd conf')
            self.connection_manager.run('echo -e "[mysqld]\nndbcluster\ndatadir=/opt/mysqlcluster/deploy/mysqld_data\nbasedir=/opt/mysqlcluster/home/mysqlc\nport=3306" > my.cnf')
            self.connection_manager.run('echo -e "[ndb_mgmd]\nhostname=manager\ndatadir=/opt/mysqlcluster/deploy/ndb_data\nnodeid=1\n\n[ndbd default]\nnoofreplicas=2\ndatadir=/opt/mysqlcluster/deploy/ndb_data\n\n[ndbd]\nhostname=worker1\nnodeid=3\n\n[ndbd]\nhostname=worker2\nnodeid=4\n\n[ndbd]\nhostname=worker3\nnodeid=5\n\n[mysqld]\nnodeid=50" > config.ini')

            # Initialize the Database
            self.connection_manager.run('cd /opt/mysqlcluster/home/mysqlc')
            self.connection_manager.run('scripts/mysql_install_db –no-defaults –datadir=/opt/mysqlcluster/deploy/mysqld_data')

            # START MANAGEMENT NODE
            self.connection_manager.run('cd /opt/mysqlcluster/home/mysqlc/bin/')
            self.connection_manager.run('ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini –initial –configdir=/opt/mysqlcluster/deploy/conf')

            # Transfer the needed files over
            self.connection_manager.put('sql_manager.py', remote='/home/ubuntu')
            self.connection_manager.put('requirements.txt', remote='/home/ubuntu')

            # Setup the flask app
            self.connection_manager.run('sudo apt update')
            self.connection_manager.run('sudo apt upgrade')

            self.connection_manager.run('sudo apt install python3')
            self.connection_manager.run('sudo apt install python3-pip')

            self.connection_manager.run('pip install -r requirements.txt')

            # Start the flask app
            self.connection_manager.run(f'python3 sql_manager.py')

            print('MySQL Cluster Manager deployment finished successfully')
        except Exception as e:
            print('Deployment Failed: ')
            print(e)
    
    def deployWorkerNode(self, connection):
        """
        Deploys MySQL Workers through SSH connection
        """
        try:
            print('Starting MySQL Workers deployment...')

            # Uninstall any existing Mysql packages
            connection.run('service mysqld stop')
            connection.run('yum remove mysql-server mysql mysql-devel')

            # Download and Extract MySQL Cluster Binaries
            connection.run('mkdir -p /opt/mysqlcluster/home')
            connection.run('cd /opt/mysqlcluster/home')
            connection.run('wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz')

            # Setup Executable Path Globally
            connection.run('echo ‘export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc’ > /etc/profile.d/mysqlc.sh')
            connection.run('echo ‘export PATH=$MYSQLC_HOME/bin:$PATH’ >> /etc/profile.d/mysqlc.sh')
            connection.run('source /etc/profile.d/mysqlc.sh')
            connection.run('sudo apt-get update && sudo apt-get -y install libncurses5')

            # Create NDB DATA directory
            connection.run('mkdir -p /opt/mysqlcluster/deploy/ndb_data')

            # START DATA NODE
            connection.run(f'ndbd -c {self.host_manager}:1186')

            # Transfer the needed files over
            connection.put('sql_worker.py', remote='/home/ubuntu')
            connection.put('requirements.txt', remote='/home/ubuntu')

            # Setup the flask app
            connection.run('sudo apt update')
            connection.run('sudo apt upgrade')

            connection.run('sudo apt install python3')
            connection.run('sudo apt install python3-pip')

            connection.run('pip install -r requirements.txt')

            # Start the flask app
            connection.run(f'python3 sql_worker.py')

            print('MySQL Cluster Worker deployment finished successfully')
        except Exception as e:
            print('Deployment Failed: ')
            print(e)

    def setupManager(self):
        # CHECK STATUS OF MGMT/DATA NODES
        self.connection_manager.run('ndb_mgm -e show')

        # START SQL NODE
        self.connection_manager.run('mysqld –defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf –user=root &')
        time.sleep(60)

        # CHECK STATUS OF MGMT/DATA NODES
        self.connection_manager.run('ndb_mgm -e show')

        # SECURE MYSQL INSTALLATION

        # Install the expect library
        self.connection_manager.run('sudo apt-get install expect')

        # Harden MySQL Server
        self.connection_manager.run('spawn sudo mysql_secure_installation')

        # Answer no to install VALIDATE PASSWORD COMPONENT
        self.connection_manager.run('expect "*:*"')
        self.connection_manager.run('send "n\r"')

        # Answer yes to remove anonymous users
        self.connection_manager.run('expect "*:*"')
        self.connection_manager.run('send "y\r"')

        # Answer yes to disable root login remotely
        self.connection_manager.run('expect "*:*"')
        self.connection_manager.run('send "y\r"')

        # Answer yes to remove test database
        self.connection_manager.run('expect "*:*"')
        self.connection_manager.run('send "y\r"')

        # Answer yes to reload privilege tables
        self.connection_manager.run('expect "*:*"')
        self.connection_manager.run('send "y\r"')

        # Download Sakila database 
        self.connection_manager.run('wget https://downloads.mysql.com/docs/sakila-db.tar.gz -O sakila-db.tar.gz')
        self.connection_manager.run('tar -xzvf sakila-db.tar.gz')
        self.connection_manager.run('cd sakila-db')

        mysql_commands = """
        CREATE DATABASE sakila;
        USE sakila;
        SOURCE sakila-schema.sql;
        SOURCE sakila-data.sql;
        SELECT * FROM sakila.actor LIMIT 10;
        EXIT;
        """
        self.connection.run(f'echo "{mysql_commands}" | mysql -u root -p root', hide=False, warn=True)



if __name__ == "__main__":
    c = Cluster()
    c.deployManagerNode()
    c.deployWorkerNode(c.connection_worker1)
    c.deployWorkerNode(c.connection_worker2)
    c.deployWorkerNode(c.connection_worker3)
    c.setupManager()