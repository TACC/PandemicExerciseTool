from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from rest_framework import viewsets
from .serializers import PETSerializer
from .models import PET
from celery.result import AsyncResult
from .pes_task import run_pes

import requests

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
        task.revoke(terminate=True)
        return JsonResponse({'task_id': task.id,}, status=200)

