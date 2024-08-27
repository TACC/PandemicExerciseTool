#!/usr/bin/env python3
import json
import requests

URL='http://localhost:8000/api/pet/'

response = requests.get(URL)
data = response.json()

for item in data:
    new_url = URL + str(item['id'])
    response = requests.delete(new_url)
    print(f'deleting id={item["id"]}, response = {response.status_code}')


