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
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis-db:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis-db:6379/0')

app = Celery('pes', broker=broker_url, backend=result_backend)

myclient = pymongo.MongoClient("mongodb://mongo-db:27017/")
mydb = myclient["PES"]
mycol = mydb["days"]
#mycol.drop()

def return_valid_input(input):
    """
    Take the json response from the get request and put it in the 
    format needed by the Pandemic exercise code
    """
    print('################')
    print(input)
    print('################')

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
      "output_dir_path": "OUTPUT",
      "number_of_realizations": "1",
      "batch_num": "0",
      'data': {
        "population": "/PES/data/STATE/county_pop_by_age_STATE_2019-2023ACS.csv",
        "contact": "/PES/data/STATE/contact_matrix_STATE_Mistry2021_all.csv",
        "flow": "/PES/data/STATE/STATE_Q4-2019_mobility-matrix.csv",
        "high_risk_ratios": "/PES/data/STATE/state_STATE_high-risk-ratios-flu-only.csv"
  
      },
      "disease_model": {
        "identity": "seatird-stochastic",
        "parameters": {
        "compartments": ["S", "E", "A", "T", "I", "R", "D"],
        "R0": "3",
        "beta_scale": "14",
        "tau": "7",
        "kappa": "2",
        "gamma": "14.0281",
        "chi": "3",
        "nu": [
            "0.002", 
            "0.002", 
            "0.002", 
            "0.002", 
            "0.002"
        ],
        "sigma": [
            "1",
            "1",
            "1",
            "1",
            "1"
        ]
        }
    },
    "travel_model": {
        "identity": "binomial",
        "parameters":{
            "rho": "1",
            "flow_reduction": [
                "1.0",
                "1.0",
                "1.0",
                "1.0",
                "1.0"
            ],
            "traveling_compartments": {
                "A": "1.0"
            },
            "transmitting_compartments": {
                "A": "1.0", 
                "T": "1.0", 
                "I": "1.0"
            }
        }
    },
    "initial_infected": json.loads(input.get("initial_infected", "[]")),
    "non_pharma_interventions": [],
    "antiviral_model": {},
    "vaccine_model": {}
    }

    input_file["disease_model"]["identity"] = input.get("model_type")

    state = input.get("state", "Texas")
    # replace STATE placeholders in paths
    input_file["output_dir_path"] = input_file["output_dir_path"].replace("STATE", state)
    for k, v in input_file["data"].items():
        input_file["data"][k] = v.replace("STATE", state)

    if input['model_type'].startswith('seatird-'):
        print('####### THIS IS SEATIRD MODEL TYPE')
        # map FLAT payload -> nested disease_model.parameters
        p = input_file["disease_model"]["parameters"]
        for key in ["R0", "beta_scale", "tau", "kappa", "gamma", "chi"]:
            if key in input and input[key] is not None:
                p[key] = str(input[key])

        # nu (allow list or comma string)
        if "nu" in input and input["nu"] is not None:
            nu = input["nu"]
            p["nu"] = [str(x) for x in (nu.split(",") if isinstance(nu, str) else nu)]

        input_file['disease_model']['parameters'] = p

    elif input['model_type'].startswith('seirs'):
        print('####### THIS IS SEIRS MODEL TYPE')
        p = {"compartments": ["S", "E", "I", "R"],
             "R0": input["R0"],
             "latent_period_days": input.get("tau", 7),
             "infectious_period_days": input.get("infectious_period", 7),
             "immune_period_days": input.get("immune_period", 120)
             }
        input_file['disease_model']['parameters'] = p

        input_file['travel_model']['parameters']['traveling_compartments'] = {'I': '0.2'}
        input_file['travel_model']['parameters']['transmitting_compartments'] = {'I': '1.0'}


    # rho into travel model
    if "rho" in input and input["rho"] is not None:
        input_file["travel_model"]["parameters"]["rho"] = str(input["rho"])

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

def try_load_json_when_ready(path, max_wait=5.0, poll=0.05):
    """
    Wait until dir is non-empty and contains valid JSON, up to max_wait seconds.
    This was an issue with the time.sleep being insufficient for TX
    """
    start = time.time()
    last_size = -1

    while time.time() - start < max_wait:
        if not os.path.exists(path):
            time.sleep(poll)
            continue

        size = os.path.getsize(path)
        if size == 0 or size != last_size:
            # size changing or empty -> still being written
            last_size = size
            time.sleep(poll)
            continue

        # size stable and non-zero: try parsing
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            time.sleep(poll)

    raise RuntimeError(f"Timed out waiting for valid JSON: {path}")

@app.task
def run_pes(input):

    # Temporary solution to get clean start per simulation
    # Clear previous run outputs
    mycol.delete_many({})

    # Remove leftover output files
    for f in glob.glob("/PES/OUTPUT/output_sim0/*"):
        if f.endswith('.json'):
            os.remove(f)

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
    max_processed_files = 200
    start_time = time.time()
    processed_files = 0

    while time.time() - start_time < max_wait_time:
        # Sorting seems necessary to prevent the variable backend output and frontend read in times
        files = sorted(glob.glob("/PES/OUTPUT/output_sim0/output_*.json"))
        time.sleep(0.05)
        # IF NEW FILE, ADD IT TO MONGO
        if len(files) > 0:
            #print(f"Processing file: {files[0]}")
            this_file = f'/PES/OUTPUT/output_sim0/output_{processed_files}.json'
            print(f'Processing file: {this_file}')
            time.sleep(0.05) # wait a bit in case data still being written to file
            try:
                mydict = try_load_json_when_ready(this_file, max_wait=5.0, poll=0.05)
                mycol.insert_one(mydict)
                processed_files += 1
                print(f"Processed day {mydict.get('day', 'unknown')}")
                os.remove(this_file)
            except Exception as e:
                print(f"Error processing file {this_file}: {e}")
                # IMPORTANT: do NOT delete the file here; let it be retried
                time.sleep(0.1)
        
        # Check if simulation is complete (usually runs for 30-90 days)
        if processed_files >= max_processed_files:  # Assume simulation is complete after N days
            break
    
    print(f"Simulation completed. Processed {processed_files} files.")
    try:
        pid = subprocess.check_output(['pgrep', '-f', 'python3 /PES/src/simulator.py'], text=True)
        os.kill(int(pid), signal.SIGKILL)
        print(f'Forcibly killing python process')
    except Exception as e:
        print(f'There was a problem exiting the process: {e}')
    for f in glob.glob("/PES/OUTPUT/output_sim0/output_*.json"):
        os.remove(f)
    return f'Simulation completed. Processed {processed_files} files.'
