#!/usr/bin/env python3
import time
from celery import Celery

app = Celery('pes', broker='pyamqp://rabbitmq')

@app.task
def run_pes(input):
    print(f'Starting with {input}')
    time.sleep(30)
    print('Done')
    return 'Done'
