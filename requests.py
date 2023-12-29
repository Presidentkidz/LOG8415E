import requests
import csv
import time

def get_Gatekeeper_ip():
        """
        Reads username and host for SSH 
        """
        with open('var/ec2_instances.csv', mode='r') as csv_file:
            # Reconstruct instances list from file
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['name'] == 'gatekeeper':
                    return (row['public_dns_name'])

URL = "http://" + get_Gatekeeper_ip() + "/new_request"

def make_read_post_request_direct_hit():
    # Send a POST request to the specified URL and return the response.
    data = {'mode': 'direct_hit', 'type': 'read', 'sql_query': 'SELECT * FROM sakila.actor LIMIT 10;'}
    response = requests.post(URL, data=data)
    return response.text

def make_read_post_request_random():
    # Send a POST request to the specified URL and return the response.
    data = {'mode': 'random', 'type': 'read', 'sql_query': 'SELECT * FROM sakila.actor LIMIT 10;'}
    response = requests.post(URL, data=data)
    return response.text

def make_read_post_request_customized():
    # Send a POST request to the specified URL and return the response.
    data = {'mode': 'customized', 'type': 'read', 'sql_query': 'SELECT * FROM sakila.actor LIMIT 10;'}
    response = requests.post(URL, data=data)
    return response.text

def make_write_post_request():
    # Send a POST request to the specified URL and return the response.
    data = {'mode': 'direct_hit', 'type': 'write', 'sql_query': 'INSERT INTO sakila.film (title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost, rating) VALUES ("Spiderman", "First Spiderman Movie", 2023, 1, 3, 4.99, 120, 19.99, "PG");'}
    response = requests.post(URL, data=data)
    return response.text

# Call the function to send the POST requests.
if __name__ == "__main__":
    print(make_read_post_request_direct_hit())
    time.sleep(10)
    print(make_read_post_request_random())
    time.sleep(10)
    print(make_read_post_request_customized())
    time.sleep(10)
    print(make_write_post_request())