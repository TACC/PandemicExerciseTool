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
                  'E_to_IPandIA_days',
                  'IP_to_IS_days',
                  'IS_to_H_days',
                  'H_to_D_days',
                  'H_to_R_days',
                  'IS_to_R_days',
                  'IA_to_R_days',
                  'prop_E_to_IA',
                  'highrisk_hosp_multiplier',
                  'prop_IS_to_H_lowrisk',
                  'prop_H_to_D',
                  'rel_inf_IP_to_IS',
                  'rel_inf_IA_to_IS',
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

