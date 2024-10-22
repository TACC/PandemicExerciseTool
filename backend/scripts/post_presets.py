#!/usr/bin/env python3
import json
import requests

POST_URL='http://localhost:8000/api/pet/'
FILENAMES=[
    'preset_slow_mild.json', 
    'preset_slow_high.json', 
    'preset_fast_mild.json', 
    'preset_fast_high.json',
    ]


def read_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def post_json(filename):
    response = requests.post(POST_URL, json=read_json(filename))
    print(f'{filename} response = {response.status_code}')

for item in FILENAMES: post_json(item)

