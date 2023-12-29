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

    if type == "write":
        cursor.execute(sql_query)

        conn.commit()

        cursor.close()
        conn.close()

        return "Write operation succeeded!"



@app.route('/')
def hello():
    return "Flask is up and running on port 80!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)