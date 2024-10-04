from rest_framework import serializers
from .models import PET


class PETSerializer(serializers.ModelSerializer):
    class Meta:
        model = PET
        fields = ('id', 
                  'disease_name', 
                  'R0', 
                  'beta_scale', 
                  'tau', 
                  'kappa', 
                  'gamma', 
                  'chi', 
                  'rho', 
                  'nu',
                  'initial_infected',
                  'npis',
                  'antiviral_effectiveness', 
                  'antiviral_wastage_factor',
                  'antiviral_stockpile',
                  'vaccine_wastage_factor',
                  'vaccine_pro_rata',
                  'vaccine_adherence',
                  'vaccine_effectiveness',
                  'vaccine_stockpile'
                  )

