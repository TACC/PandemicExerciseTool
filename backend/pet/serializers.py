from rest_framework import serializers
from .models import PET


class PETSerializer(serializers.ModelSerializer):
    class Meta:
        model = PET
        fields = ('id', 
                  'disease_name',
                  'model_type',
                  'state',
                  'R0', 
                  'beta_scale', 
                  'tau',
                  'kappa',
                  'gamma',
                  'chi',
                  'rho',
                  'nu',
                  'sigma',
                  'infectious_period',
                  'immune_period',
                  'initial_infected',
                  'npis',
                  'vaccine_model',
                  'vaccine_priority_groups',
                  'vaccine_capacity',
                  'vaccine_effectiveness_lag',
                  'vaccine_effectiveness',
                  'vaccine_adherence',
                  'vaccine_stockpile',
                  )

