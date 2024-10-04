#!/usr/bin/env python3
import json
import requests

ID=5
GET_URL=f'http://localhost:8000/api/pet/{ID}'
RUN_URL=f'http://localhost:8000/api/pet/{ID}/run'


response = requests.get(GET_URL)
data = response.json()
print(f'response = {response.status_code}')
print(f'data[phas] = {data["phas"]}')

try: phas = json.loads(data['phas'])
except TypeError: phas = None

try: avs = json.loads(data['phas'])
except TypeError: avs = None

try: va = json.loads(data['phas'])
except TypeError: va = None

try: ve = json.loads(data['phas'])
except TypeError: ve = None

try: vs = json.loads(data['phas'])
except TypeError: vs = None


input_file = {
  'output': 'OUTPUT.json',
  'number_of_realizations': '1',
  'data': {
    'population': '/PES/data/texas/county_age_matrix_small.csv',
    'contact': '/PES/data/texas/contact_matrix.csv',
    'flow': '/PES/data/texas/work_matrix_rel.csv',
    'high_risk_ratios': '/PES/data/texas/high_risk_ratios.csv',
    'flow_reduction': '/PES/data/texas/flow_reduction.csv',
    'relative_susceptibility': '/PES/data/texas/relative_susceptibility.csv',
    'nu_value_matrix': '/PES/data/texas/nu_value_matrix.csv'
  },
  'parameters': {
    'R0': data['R0'],
    'beta_scale': data['beta_scale'],
    'tau': data['tau'],
    'kappa': data['kappa'],
    'gamma': data['gamma'],
    'chi': data['chi'],
    'rho': data['rho'],
    'nu': data['nu'] 
  },
  'initial_infected': json.loads(data['initial_infected']),
  'non_pharma_interventions': phas,
  'antivirals': {
    'antiviral_effectiveness': data['antiviral_effectiveness'],
    'antiviral_wastage_factor': data['antiviral_wastage_factor'],
    'antiviral_stockpile': avs
  },
  'vaccines': {
    'vaccine_wastage_factor': data['vaccine_wastage_factor'],
    'vaccine_pro_rata': data['vaccine_pro_rata'],
    'vaccine_adherence': va,
    'vaccine_effectiveness': ve,
    'vaccine_stockpile': vs 
  }
}


with open('FINAL.json', 'w') as o:
    json.dump(input_file, o, indent=2)
