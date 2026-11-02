from rest_framework import status
from rest_framework.test import APITestCase

from .models import PET


class SimulationCreationTests(APITestCase):
    def test_create_simulation_with_legacy_and_seihrd_parameters(self):
        """Play must be able to save both models after schema upgrades."""
        payload = {
            'disease_name': 'Test scenario',
            'model_type': 'seirs-deterministic',
            'state': 'Texas',
            'R0': 1.2,
            'beta_scale': 10.0,
            'tau': 1.2,
            'kappa': 1.9,
            'gamma': 4.1,
            'chi': 1.0,
            'rho': 0.39,
            'nu': '0,0,0,0,0',
            'sigma': '1,1,1,1,1',
            'infectious_period': 14,
            'immune_period': 0,
            'initial_infected': '[]',
            'npis': '[]',
        }
        for extra in ({}, {
            'model_type': 'seihrd-deterministic',
            'E_to_IPandIA_days': 0.7,
            'H_to_R_days': '[7,7,7,7,7]',
        }):
            with self.subTest(model=extra.get('model_type', payload['model_type'])):
                response = self.client.post('/api/pet/', {**payload, **extra}, format='json')

                self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
                simulation = PET.objects.get(pk=response.data['id'])
                self.assertEqual(simulation.model_type, extra.get('model_type', payload['model_type']))
                self.assertEqual(simulation.E_to_IPandIA_days, extra.get('E_to_IPandIA_days'))
                self.assertEqual(simulation.H_to_R_days, extra.get('H_to_R_days'))
