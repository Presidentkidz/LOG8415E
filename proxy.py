from flask import Flask, request, jsonify
import random
import string
import re
import requests
import sys
from ping3 import ping, verbose_ping

app = Flask(__name__)
    
@app.route('/new_request', methods=['POST'])

def new_request():
    data = request.json  # or request.get_json()

    mode = data['mode']
    type = data['type']
    sql_query = data['sql_query']

    if type == "write":
        direct_hit_request(type, sql_query)

    if type == "read":
        if mode == "direct_hit":
            return direct_hit_request(type, sql_query)
        if mode == "random":
            return random_request(type, sql_query)
        if mode == "customized":
            return customized_request(type, sql_query)

# Direct all requests to the manager
def direct_hit_request(type, sql_query):
    manager_dns = sys.argv[1]

    manager_url = "http://" + manager_dns + "/new_request"

    data = {'type': type, 'sql_query': sql_query} 

    response = requests.post(manager_url, data=data)

    return response.text

# Randomly select a worker
def random_request(type, sql_query):
    # Put all 3 workers in a list
    workers_dns = [sys.argv[2], sys.argv[3], sys.argv[4]]
    worker_dns = random.choice(workers_dns)

    worker_url = "http://" + worker_dns + "/new_request"

    data = {'type': type, 'sql_query': sql_query} 

    response = requests.post(worker_url, data=data)

    return response.text

# Mesure the worker with least ping time
def customized_request(type, sql_query):
    worker1_dns = sys.argv[2]
    worker2_dns = sys.argv[3]
    worker3_dns = sys.argv[4]

    lowest_dns

    # Determine the lowest ping
    if measure_ping(worker1_dns) <= measure_ping(worker2_dns) and measure_ping(worker1_dns) <= measure_ping(worker3_dns):
        lowest_dns = worker1_dns

    elif measure_ping(worker2_dns) <= measure_ping(worker1_dns) and measure_ping(worker2_dns) <= measure_ping(worker3_dns):
        lowest_dns = worker2_dns

    else:
        lowest_dns = worker3_dns

    lowest_url = "http://" + lowest_dns + "/new_request"

    data = {'type': type, 'sql_query': sql_query} 

    response = requests.post(lowest_url, data=data)

    return response.text

def measure_ping(host):
    response_time = ping(host)  # Ping the server, returns the response time in seconds
    if response_time is None:
        print(f"Failed to ping {host}")
        return 9999
    else:
        print(f"Ping time to {host}: {response_time * 1000:.2f} ms")
        return response_time * 1000

@app.route('/')
def hello():
    return "Flask is up and running on port 80!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)