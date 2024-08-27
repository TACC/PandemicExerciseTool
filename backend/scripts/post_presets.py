#!/usr/bin/env python3
import json
import requests

POST_URL='http://localhost:8000/api/pet/'
FILENAMES=['slow_mild.json', 'slow_high.json', 'fast_mild.json', 'fast_high.json']


def read_json(filename):
    with open(filename, 'r') as i:
        return json.load(i)

def post_json(filename):
    response = requests.post(POST_URL, json=read_json(filename))
    print(f'{filename} response = {response.status_code}')

for item in FILENAMES: post_json(item)

