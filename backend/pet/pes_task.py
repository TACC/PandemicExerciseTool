#!/usr/bin/env python3
import time
import json
import logging
from celery import Celery
import subprocess
import glob
import os
import pymongo
import redis
import signal
from ctypes import cdll
from .texasMapping import texas_mapping

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get broker URL from environment variable or use default
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis-db:6379/0')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis-db:6379/0')

app = Celery('pes', broker=broker_url, backend=result_backend)

myclient = pymongo.MongoClient("mongodb://mongo-db:27017/")
mydb = myclient["PES"]
mycol = mydb["days"]
#mycol.drop()

# Shared pause/resume signaling, keyed by Celery task id. Django sets/clears
# this key via the same Redis instance; run_pes polls it to freeze/thaw the
# simulator subprocess in place instead of killing it.
redis_client = redis.Redis.from_url(broker_url)
PAUSE_KEY_PREFIX = 'pause:'
MAX_PAUSE_SECONDS = 900  # auto-cancel a run left paused longer than this


def pause_key(task_id):
    return f'{PAUSE_KEY_PREFIX}{task_id}'


def is_paused(task_id):
    return bool(redis_client.get(pause_key(task_id)))


def return_valid_input(input):
    """
    Take the json response from the post request and put it in the
    format needed by the Pandemic exercise code
    """
    logging.info('Parsing input from post request')
    logging.info(input)


    
    #try:
    #    avs = json.loads(input['antiviral_stockpile'])
    #except (TypeError, json.JSONDecodeError):
    #    avs = None
    
    input_file = {
      "output_dir_path": "OUTPUT",
      "number_of_realizations": "1",
      "batch_num": "0",
      'data': {
        "population": "/PES/data/STATE/county_pop_by_age_STATE_2019-2023ACS.csv",
        "contact": "/PES/data/STATE/contact_matrix_STATE_Mistry2021_all.csv",
        "flow": "/PES/data/STATE/STATE_Q4-2019_mobility-matrix.csv",
        "high_risk_ratios": "/PES/data/STATE/state_STATE_high-risk-ratios-flu-only.csv",
      },
      "disease_model": {
        "identity": input.get("model_type"),
        "parameters": {
        "compartments": ["S", "E", "A", "T", "I", "R", "D"],
        "R0": "3",
        "beta_scale": "14",
        "tau": "7",
        "kappa": "2",
        "gamma": "14.0281",
        "chi": "3",
        "nu": [ "0.002", "0.002", "0.002", "0.002", "0.002" ],
        "sigma": [ "1", "1", "1", "1", "1" ]
        }
    },
    "travel_model": {
        "identity": "binomial",
        "parameters":{
            "rho": "1",
            "flow_reduction": [ "1.0", "1.0", "1.0", "1.0", "1.0" ],
            "traveling_compartments": { "A": "1.0" },
            "transmitting_compartments": { "A": "1.0", "T": "1.0", "I": "1.0" }
        }
    },
    "initial_infected": json.loads(input.get("initial_infected", "[]")),
    "non_pharma_interventions": [],
    "antiviral_model": {},
    "vaccine_model": {}
    }

    #input_file["disease_model"]["identity"] = input.get("model_type")

    # replace STATE placeholders in paths
    state = input.get("state", "Texas")
    input_file["output_dir_path"] = input_file["output_dir_path"].replace("STATE", state)
    for k, v in input_file["data"].items():
        input_file["data"][k] = v.replace("STATE", state)

    if input['model_type'].startswith('seaitrd-'):
        print('####### THIS IS SEAITRD MODEL TYPE')
        # map FLAT payload -> nested disease_model.parameters
        p = input_file["disease_model"]["parameters"]
        for key in ["R0", "beta_scale", "tau", "kappa", "gamma", "chi"]:
            if key in input and input[key] is not None:
                p[key] = str(input[key])

        # nu (allow list or comma string)
        if "nu" in input and input["nu"] is not None:
            nu = input["nu"]
            p["nu"] = [str(x) for x in (nu.split(",") if isinstance(nu, str) else nu)]

        # sigma (allow list or comma string)
        if "sigma" in input and input["sigma"] is not None:
            sigma = input["sigma"]
            p["sigma"] = [str(x) for x in (sigma.split(",") if isinstance(sigma, str) else sigma)]

        input_file['disease_model']['parameters'] = p

    elif input['model_type'].startswith('seirs'):
        p = {"compartments": ["S", "E", "I", "R"],
             "R0": input["R0"],
             "latent_period_days": input.get("tau", 7),
             "infectious_period_days": input.get("infectious_period", 7),
             "immune_period_days": input.get("immune_period", 120)
             }
        input_file['disease_model']['parameters'] = p

        input_file['travel_model']['parameters']['traveling_compartments'] = {'I': '1.0'}
        input_file['travel_model']['parameters']['transmitting_compartments'] = {'I': '1.0'}

    # rho into travel model
    if "rho" in input and input["rho"] is not None:
        input_file["travel_model"]["parameters"]["rho"] = str(input["rho"])


    # Put NPIs into input file
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
        npis = []

    input_file['npis'] = npis


    # Put vaccine model bits into input file
    if input['vaccine_model'] == '{}':
        vm = {}
    else:
        vm = {
            'identity': input['vaccine_model'],
            'parameters': {
                'age_risk_priority_groups': json.loads(input['vaccine_priority_groups']),
                'vaccine_half_life_days': None,
                'vaccine_capacity_proportion': input['vaccine_capacity'],
                'vaccine_adherence': json.loads(input['vaccine_adherence']),
                'vaccine_effectiveness': json.loads(input['vaccine_effectiveness']),
                'vaccine_eff_lag_days': input['vaccine_effectiveness_lag'],
                'vaccine_stockpile': json.loads(input['vaccine_stockpile']),
            }
        }

    input_file['vaccine_model'] = vm

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


@app.task(bind=True)
def run_pes(self, input):
    task_id = self.request.id

    # Temporary solution to get clean start per simulation
    # Clear previous run outputs
    mycol.delete_many({})

    # Remove leftover output files
    for f in glob.glob("/PES/OUTPUT/output_sim0/*"):
        if f.endswith('.json'):
            os.remove(f)

    os.chdir('/PES')

    # Format api request into valid input file
    input_file = return_valid_input(input)
    with open('/PES/INPUT.json', 'w') as o:
        json.dump(input_file, o, indent=2)

    logging.info('Wrote INPUT.json to file, contents are:')
    logging.info(json.dumps(input_file, indent=2))

    # Simulation subrocess start
    proc = subprocess.Popen(['python3',
                      '/PES/src/simulator.py',
                      '--input',
                      '/PES/INPUT.json',
                      '--days',
                      '200',
                      '--loglevel',
                      'INFO'],
                      preexec_fn=on_parent_exit('SIGHUP'))

    # Simulation control
    max_wait_time = 600  # Maximum wait time in seconds (10 minutes), excludes paused time
    max_processed_files = 200
    start_time = time.time()
    processed_files = 0
    paused_duration = 0.0
    is_stopped = False
    pause_started = None
    cancelled_while_paused = False

    while time.time() - start_time - paused_duration < max_wait_time:
        if is_paused(task_id):
            if not is_stopped:
                logging.info(f'Pausing simulation (task {task_id})')
                os.kill(proc.pid, signal.SIGSTOP)
                is_stopped = True
                pause_started = time.time()

            if time.time() - pause_started > MAX_PAUSE_SECONDS:
                logging.warning(
                    f'Simulation (task {task_id}) paused longer than '
                    f'{MAX_PAUSE_SECONDS}s; cancelling'
                )
                cancelled_while_paused = True
                break

            time.sleep(0.5)
            continue
        elif is_stopped:
            logging.info(f'Resuming simulation (task {task_id})')
            os.kill(proc.pid, signal.SIGCONT)
            paused_duration += time.time() - pause_started
            is_stopped = False
            pause_started = None

        # Sorting seems necessary to prevent the variable backend output and frontend read in times
        files = sorted(glob.glob("/PES/OUTPUT/output_sim0/output_*.json"))
        time.sleep(0.05)

        # If new file found, add it to mongo
        if len(files) > 0:
            this_filename = f'/PES/OUTPUT/output_sim0/output_{processed_files}.json'
            logging.info(f'Processing file: {this_filename}')
            time.sleep(0.05) # wait a bit in case data still being written to file

            try:
                this_output = try_load_json_when_ready(this_filename, max_wait=5.0, poll=0.05)
                mycol.insert_one(this_output)
                processed_files += 1
                print(f"Processed day {this_output.get('day', 'unknown')}")
                os.remove(this_filename)

            except Exception as e:
                print(f"Error processing file {this_filename}: {e}")
                # IMPORTANT: do NOT delete the file here; let it be retried
                time.sleep(0.1)

        # Check if simulation is complete (usually runs for 30-90 days)
        if processed_files >= max_processed_files:
            break

    # Clear the pause flag so it doesn't linger for a future task with a reused id
    redis_client.delete(pause_key(task_id))

    if cancelled_while_paused:
        logging.info(f"Simulation (task {task_id}) cancelled after an extended pause.")
    else:
        logging.info(f"Simulation completed. Processed {processed_files} files.")

    # Clean up process if it is still running (SIGKILL works even if it's currently stopped)
    try:
        pid = subprocess.check_output(['pgrep', '-f', 'python3 /PES/src/simulator.py'], text=True)
        os.kill(int(pid), signal.SIGKILL)
    except Exception as e:
        logging.warning(f'There was a problem exiting the process: {e}')

    # Make sure all old output files are removed
    for f in glob.glob("/PES/OUTPUT/output_sim0/output_*.json"):
        os.remove(f)

    if cancelled_while_paused:
        return f'Simulation cancelled after an extended pause. Processed {processed_files} files.'
    return f'Simulation completed. Processed {processed_files} files.'
