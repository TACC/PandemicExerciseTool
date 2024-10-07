from django.shortcuts import render
from django.http import JsonResponse

from rest_framework import viewsets
from .serializers import PETSerializer
from .models import PET
from celery.result import AsyncResult
from .pes_task import run_pes, app

import requests
import pymongo

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
        return JsonResponse({'task_id': task.id,}, status=200)

def get_output(request, day):
    if request.method == 'GET':
        mydoc = mycol.find_one({'day': int(day)})
        if mydoc is None:
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
