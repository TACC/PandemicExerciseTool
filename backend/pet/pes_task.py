#!/usr/bin/env python3
import time
import json
from celery import Celery

app = Celery('pes', broker='pyamqp://rabbitmq')

def return_valid_input(input):
    """
    Take the json response from the get request and put it in the 
    format needed by the Pandemic exercise code
    """
    try: phas = json.loads(input['phas'])
    except TypeError: phas = None
    
    try: avs = json.loads(input['phas'])
    except TypeError: avs = None
    
    try: va = json.loads(input['phas'])
    except TypeError: va = None
    
    try: ve = json.loads(input['phas'])
    except TypeError: ve = None
    
    try: vs = json.loads(input['phas'])
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
        'R0': input['R0'],
        'beta_scale': input['beta_scale'],
        'tau': input['tau'],
        'kappa': input['kappa'],
        'gamma': input['gamma'],
        'chi': input['chi'],
        'rho': input['rho'],
        'nu': input['nu'] 
      },
      'initial_infected': json.loads(input['initial_infected']),
      'public_health_announcements': phas,
      'antivirals': {
        'antiviral_effectiveness': input['antiviral_effectiveness'],
        'antiviral_wastage_factor': input['antiviral_wastage_factor'],
        'antiviral_stockpile': avs
      },
      'vaccines': {
        'vaccine_wastage_factor': input['vaccine_wastage_factor'],
        'vaccine_pro_rata': input['vaccine_pro_rata'],
        'vaccine_adherence': va,
        'vaccine_effectiveness': ve,
        'vaccine_stockpile': vs 
      }
    }

    return input_file


@app.task
def run_pes(input):
    #print(f'Starting with {input}')
    time.sleep(30)
    input_file = return_valid_input(input)
    with open('INPUT.json', 'w') as o:
        json.dump(input_file, o, indent=2)
    print('Wrote INPUT.json to file, contents are:')
    print(json.dumps(input_file, indent=2))
    print('Now running PES code.....')
    time.sleep(30)
    return 'Done'
