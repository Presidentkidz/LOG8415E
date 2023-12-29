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

    mode_validator = validate_mode_input(mode)
    type_validator = validate_type_input(type)
    sql_validator = validate_sql_input(sql_query)

    if mode_validator == True and type_validator == True and sql_validator == True:
        return send_request_to_trusted_host(mode, type, sql_query)

def validate_mode_input(input):
    if input == "direct_hit" or input == "random" or input == "customized":
        return True
    else:
        return False

def validate_type_input(input):
    if input == "read" or input == "write":
        return True
    else:
        return False
    
def validate_sql_input(input):
    # Simple regex pattern to detect basic SQL injection attempts
    # This pattern is basic and may not catch advanced injection attempts
    suspicious_patterns = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",  # Attempt to unescape single quotes, comments
        r"((\%3D)|=)[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",  # Basic SQL meta-characters
        r"\w*((\%27)|(\'))(\%6F|%4F)(\%72|%52)",  # Typical 'or' statement used in SQL injection
        r"(\%27)|(\')|(\-\-)|(\%3B)|(;)"  # Basic SQL injection characters
    ]

    # Check for suspicious patterns
    for pattern in suspicious_patterns:
        if re.search(pattern, input, re.IGNORECASE):
            return False

    return True

def send_request_to_trusted_host(mode, type, sql_query):
    if len(sys.argv) > 1:
        trusted_host_dns = sys.argv[1]

        trusted_host_url = "http://" + trusted_host_dns + "/new_request"

        data = {'mode': mode, 'type': type, 'sql_query': sql_query} 

        response = requests.post(trusted_host_url, data=data)

        return response.text

@app.route('/')
def hello():
    return "Flask is up and running on port 80!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)