from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from rest_framework import viewsets
from .serializers import PETSerializer
from .models import PET
from celery.result import AsyncResult
from .pes_task import run_pes, app, redis_client, pause_key

import requests
import pymongo

import logging


logger = logging.getLogger(__name__)

myclient = pymongo.MongoClient("mongodb://mongo-db:27017/")
mydb = myclient["PES"]
mycol = mydb["days"]


class PETView(viewsets.ModelViewSet):
    serializer_class = PETSerializer
    queryset = PET.objects.all()

def run_job(request, pet_id):
    if request.method == 'GET':
        input = requests.get(f'http://localhost:8000/api/pet/{pet_id}/').json()
        task = run_pes.delay(input)
        return JsonResponse({'task_id': task.id,}, status=202)

def delete_job(request, task_id):
    if request.method == 'GET':
        task = AsyncResult(task_id)
        task.revoke(terminate=True, signal='SIGKILL')
        redis_client.delete(pause_key(task_id))
        return JsonResponse({'task_id': task.id,}, status=200)

def pause_job(request, task_id):
    if request.method == 'GET':
        redis_client.set(pause_key(task_id), '1')
        return JsonResponse({'task_id': task_id, 'paused': True}, status=200)

def resume_job(request, task_id):
    if request.method == 'GET':
        redis_client.delete(pause_key(task_id))
        return JsonResponse({'task_id': task_id, 'paused': False}, status=200)

def get_output(request, day):
    if request.method == 'GET':
        mydoc = mycol.find_one({'day': int(day)})
        if mydoc is None:
            logger.warning(f"Day {day} not calculated")
            return JsonResponse(
                {"error": f"Day {day} not calculated"},
                status=404
            )
        del mydoc['_id']
        return JsonResponse(mydoc, status=200)

def reset_state(request):
    if request.method == 'GET':
        mycol.delete_many({})
        app.control.purge()
        return JsonResponse({'result': 'State Reset'}, status=200)

def home(request):
    return HttpResponse("""
    <h1>Pandemic Exercise Tool API</h1>
    <p>Backend is running successfully!</p>
    <h2>Available Endpoints:</h2>
    <ul>
        <li><a href="/api/">/api/</a> - API Root</li>
        <li><a href="/api/pet/">/api/pet/</a> - List simulations</li>
        <li>/api/pet/&lt;id&gt;/run - Run simulation</li>
        <li>/api/pause/&lt;task_id&gt; - Pause a running simulation</li>
        <li>/api/resume/&lt;task_id&gt; - Resume a paused simulation</li>
        <li>/api/output/&lt;day&gt; - Get simulation output</li>
        <li><a href="/api/reset">/api/reset</a> - Reset simulation state</li>
        <li><a href="/admin/">/admin/</a> - Admin interface</li>
    </ul>
    <p>Dash Frontend: <a href="http://localhost:8050">http://localhost:8050</a></p>
    """)
