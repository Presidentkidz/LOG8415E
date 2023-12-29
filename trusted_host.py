from flask import Flask, request, jsonify
import random
import string
import re
import requests
import sys

app = Flask(__name__)
    
@app.route('/new_request', methods=['POST'])

def new_request():
    data = request.json  # or request.get_json()

    mode = data['mode']
    type = data['type']
    sql_query = data['sql_query']

    return send_request_to_proxy(mode, type, sql_query)

def send_request_to_proxy(mode, type, sql_query):
    if len(sys.argv) > 1:
        proxy_dns = sys.argv[1]

        proxy_url = "http://" + proxy_dns + "/new_request"

        data = {'mode': mode, 'type': type, 'sql_query': sql_query} 

        response = requests.post(proxy_url, data=data)

        return response.text

@app.route('/')
def hello():
    return "Flask is up and running on port 80!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)