#!/bin/bash

# Create ec2 instances
echo "Creating 1 standalone SQL t2.micro + 1 t2.micro for SQL manager + 3 t2.micro for SQL workers"
python3 ec2.py 

# Create standalone SQL
echo "Creating standalone SQL server"
python3 standalone_sql.py 


