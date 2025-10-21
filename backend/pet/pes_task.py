#!/usr/bin/env python3
import time
import json
from celery import Celery
import subprocess
import glob
import os
import pymongo
import signal
from ctypes import cdll
from .texasMapping import texas_mapping

# Get broker URL from environment variable or use default
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

app = Celery('pes', broker=broker_url, backend=result_backend)

myclient = pymongo.MongoClient("mongodb://mongo-db-dash:27017/")
mydb = myclient["PES"]
mycol = mydb["days"]
#mycol.drop()


def return_valid_input(input):
    """
    Take the json response from the get request and put it in the 
    format needed by the Pandemic exercise code
    """
    try:
        if input['npis'] is not None:
            npis = json.loads(input['npis'])
            for index, npi in enumerate(npis):
                new_list = []
                # Handle location - can be string or list
                location = npi['location']
                if isinstance(location, str):
                    counties = location.split(',')
                elif isinstance(location, list):
                    counties = location
                else:
                    counties = [str(location)]
                
                for county in counties:
                    if county in texas_mapping:
                        new_county = texas_mapping[county]
                        new_list.append(new_county)
                    else:
                        print(f"Warning: County '{county}' not found in mapping")
                        new_list.append('1')  # Default to Anderson County
                npis[index]['location'] = (',').join(new_list)
                
                # Handle effectiveness - can be string or list
                effectiveness = npi['effectiveness']
                if isinstance(effectiveness, str):
                    eff_list = effectiveness.split(',')
                elif isinstance(effectiveness, list):
                    eff_list = [str(x) for x in effectiveness]
                else:
                    eff_list = [str(effectiveness)]
                npis[index]['effectiveness'] = eff_list
        else:
            npis = []
    except (TypeError, KeyError, json.JSONDecodeError) as e:
        print(f"Error processing NPIs: {e}")
        npis = None
    
    try: 
        avs = json.loads(input['antiviral_stockpile'])
    except (TypeError, json.JSONDecodeError): 
        avs = None
    
    try: 
        va = json.loads(input['vaccine_adherence'])
    except (TypeError, json.JSONDecodeError): 
        va = None
    if va is not None:
        va = [va] * 5
    
    try: 
        ve = json.loads(input['vaccine_effectiveness'])
    except (TypeError, json.JSONDecodeError): 
        ve = None
    if ve is not None:
        ve = [ve] * 5
    
    try: 
        vs = json.loads(input['vaccine_stockpile'])
    except (TypeError, json.JSONDecodeError): 
        vs = None
    
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
        'nu': input['nu'].split(',') if isinstance(input['nu'], str) else input['nu']
      },
      'initial_infected': json.loads(input.get('initial_infected', '[]')),
      'non_pharma_interventions': npis,
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


def on_parent_exit(signame):
    """
    Make sure child is killed when parent is killed. Adapted from
    https://gist.github.com/evansd/2346614
    """
    signum = getattr(signal, signame)
    def set_parent_exit_signal():
        result = cdll['libc.so.6'].prctl(1, signum)
    return set_parent_exit_signal


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
                      'INFO'],
                      preexec_fn=on_parent_exit('SIGHUP'))
    
    max_wait_time = 300  # Maximum wait time in seconds (5 minutes)
    start_time = time.time()
    processed_files = 0
    
    while time.time() - start_time < max_wait_time:
        files = glob.glob("/PES/OUTPUT*")
        time.sleep(0.5)
        # IF NEW FILE, ADD IT TO MONGO
        if len(files) > 0:
            print(f"Processing file: {files[0]}")
            time.sleep(1)
            try:
                with open(files[0], 'r') as f:
                    mydict = json.load(f)
                    mycol.insert_one(mydict)
                    processed_files += 1
                    print(f"Processed day {mydict.get('day', 'unknown')}")
                    os.remove(files[0])
            except Exception as e:
                print(f"Error processing file {files[0]}: {e}")
                os.remove(files[0])  # Remove problematic file
        
        # Check if simulation is complete (usually runs for 30-90 days)
        if processed_files >= 90:  # Assume simulation is complete after 90 days
            break
    
    print(f"Simulation completed. Processed {processed_files} files.")
    return f'Simulation completed. Processed {processed_files} files.'
