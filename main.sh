#!/bin/bash

# Create ec2 instances
echo "Creating ec2 instances"
python3 ec2.py 

# Create standalone SQL
echo "Creating standalone SQL server"
python3 standalone_sql.py 

# Create SQL Cluster
echo "Creating standalone SQL server"
python3 mysql_cluster.py 

# Gatekeeper setup
echo "Setting up Gatekeeper"
python3 gatekeeper_setup.py 

# Trusted host setup
echo "Setting up Trusted host"
python3 trusted_host_setup.py 

# Proxy setup
echo "Setting up Proxy"
python3 proxy_setup.py 

# Sending SQL requests to Gatekeeper
echo "Sending SQL requests to Gatekeeper"
python3 requests.py 


