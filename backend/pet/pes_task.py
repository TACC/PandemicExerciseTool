#!/usr/bin/env python3
import time
import json
from celery import Celery
import subprocess
import glob
import os
import pymongo

app = Celery('pes', broker='pyamqp://rabbitmq')

myclient = pymongo.MongoClient("mongodb://mongo-db:27017/")
mydb = myclient["PES"]
mycol = mydb["days"]
mycol.drop() # I think this deletes all the data


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
    os.chdir('/PES')
    input_file = return_valid_input(input)
    with open('/PES/INPUT.json', 'w') as o:
        json.dump(input_file, o, indent=2)
    print('Wrote INPUT.json to file, contents are:')
    print(json.dumps(input_file, indent=2))
    print('Now running PES code.....')

    subprocess.Popen(['python3',
                      '/PES/src/simulator.py',
                      '--input',
                      '/PES/INPUT.json',
                      '--days',
                      '999',
                      '--loglevel',
                      'INFO'])
    
    while True:
        files=glob.glob("/PES/OUTPUT*")
        print(files)
        # IF NEW FILE, ADD IT TO MONGO
        if len(files) > 0:
            with open(files[0], 'r') as f:
                mydict = json.load(f)
                mycol.insert_one(mydict)
                os.remove(files[0])
        time.sleep(1)

    return 'Done'