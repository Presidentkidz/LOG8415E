from flask import Flask, request, jsonify
import random
import string
import re
import requests
import sys
import mysql.connector

app = Flask(__name__)
    
@app.route('/new_request', methods=['POST'])

def new_request():
    data = request.json  # or request.get_json()

    type = data['type']
    sql_query = data['sql_query']

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="sakila"
    )

    cursor = conn.cursor()

    if type == "read":
        cursor.execute(sql_query)

        # Fetch column names
        column_names = [column[0] for column in cursor.description]
    
        # Convert each row into a dictionary
        results = [dict(zip(column_names, row)) for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        # Return the results as a JSON response
        return jsonify(results)



@app.route('/')
def hello():
    return "Flask is up and running on port 80!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)