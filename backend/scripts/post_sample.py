#!/usr/bin/env python3
import json
import requests

POST_URL='http://localhost:8000/api/pet/'
FILENAME='INPUT_small.json'

data={}
data_to_post={}


with open(FILENAME, 'r') as i:
    data = json.load(i)


data_to_post['disease_name'] = FILENAME
data_to_post['R0'] = data['parameters']['R0']
data_to_post['beta_scale'] = data['parameters']['beta_scale']
data_to_post['tau'] = data['parameters']['tau']
data_to_post['kappa'] = data['parameters']['kappa']
data_to_post['gamma'] = data['parameters']['gamma']
data_to_post['chi'] = data['parameters']['chi']
data_to_post['rho'] = data['parameters']['rho']
data_to_post['nu'] = data['parameters']['nu']
data_to_post['initial_infected'] = json.dumps(data['initial_infected'])


print(data)
print('')
print(data_to_post)
print('')


response = requests.post(POST_URL, json=data_to_post)
print(f'response = {response.status_code}')



