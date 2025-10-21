import requests
import json
import logging
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class PandemicAPIClient:
    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.base_url = base_url
        self.session = requests.Session()
        
    def create_simulation(self, parameters: Dict[str, Any]) -> Optional[str]:
        """Create a new simulation with given parameters"""
        try:
            url = f"{self.base_url}/api/pet/"
            response = self.session.post(url, json=parameters)
            response.raise_for_status()
            
            data = response.json()
            return data.get('id')
        except requests.RequestException as e:
            logger.error(f"Error creating simulation: {e}")
            return None
    
    def run_simulation(self, simulation_id: str) -> Optional[str]:
        """Start running a simulation"""
        try:
            url = f"{self.base_url}/api/pet/{simulation_id}/run"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data.get('task_id')
        except requests.RequestException as e:
            logger.error(f"Error running simulation: {e}")
            return None
    
    def stop_simulation(self, task_id: str) -> bool:
        """Stop a running simulation"""
        try:
            url = f"{self.base_url}/api/delete/{task_id}"
            response = self.session.get(url)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Error stopping simulation: {e}")
            return False
    
    def get_simulation_output(self, day: int) -> Optional[Dict[str, Any]]:
        """Get simulation output for a specific day"""
        try:
            url = f"{self.base_url}/api/output/{day}"
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            if response.status_code != 404:  # 404 is expected when data not ready
                logger.error(f"Error getting simulation output for day {day}: {e}")
            return None
    
    def reset_state(self) -> bool:
        """Reset the simulation state"""
        try:
            url = f"{self.base_url}/api/reset"
            response = self.session.get(url)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Error resetting state: {e}")
            return False
    
    def format_simulation_parameters(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format form data into simulation parameters"""
        # Format initial infected counties
        initial_infected = []
        if form_data.get('initial_counties') and form_data.get('initial_cases_count'):
            for county_fips in form_data['initial_counties']:
                initial_infected.append({
                    'fips_id': county_fips,
                    'cases': form_data['initial_cases_count']
                })
        
        # Format NPIs
        npis = []
        if form_data.get('npi_checklist'):
            for npi in form_data['npi_checklist']:
                npis.append({
                    'type': npi,
                    'effectiveness': 0.5,  # Default effectiveness
                    'start_day': 5,  # Default start day
                    'duration': 30  # Default duration
                })
        
        parameters = {
            'disease_name': form_data.get('disease_name', 'COVID-19'),
            'R0': form_data.get('reproduction_number', 2.5),
            'beta_scale': form_data.get('beta_scale', 1.0),
            'tau': form_data.get('tau', 5.1),
            'kappa': form_data.get('kappa', 1.0),
            'gamma': form_data.get('gamma', 0.1),
            'chi': form_data.get('chi', 0.5),
            'rho': form_data.get('rho', 0.8),
            'nu': form_data.get('nu', 0.01),
            'initial_infected': json.dumps(initial_infected),
            'npis': json.dumps(npis),
            'vaccine_effectiveness': form_data.get('vaccine_effectiveness', 85) / 100,
            'vaccine_adherence': form_data.get('vaccine_adherence', 70) / 100,
            'vaccine_stockpile': form_data.get('vaccine_stockpile', 1000000),
            'vaccine_wastage_factor': form_data.get('vaccine_wastage', 0.1),
            'vaccine_pro_rata': form_data.get('vaccine_strategy', 'proportional'),
            'antiviral_effectiveness': form_data.get('antiviral_effectiveness', 75) / 100,
            'antiviral_stockpile': form_data.get('antiviral_stockpile', 500000),
            'antiviral_wastage_factor': form_data.get('antiviral_wastage', 0.05),
        }
        
        return parameters