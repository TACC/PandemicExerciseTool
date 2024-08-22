from django.shortcuts import render
from rest_framework import viewsets
from .serializers import PETSerializer
from .models import PET

# Create your views here.

class PETView(viewsets.ModelViewSet):
    serializer_class = PETSerializer
    queryset = PET.objects.all()
