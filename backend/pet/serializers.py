from rest_framework import serializers
from .models import PET

class PETSerializer(serializers.ModelSerializer):
    class Meta:
        model = PET
        fields = ('id', 'disease_name', 'reproduction_number', 'beta_scale', 'tau', 
                  'kappa', 'gamma', 'chi', 'rho', 'nu',
                  'vaccine_wastage_factor', 'antiviral_effectiveness', 'antiviral_wastage_factor')
