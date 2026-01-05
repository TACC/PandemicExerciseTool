import json
import pandas as pd
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DataLoader:
    """Handles loading and parsing of Texas counties and other data files"""
    
    def __init__(self, data_path: str = "../frontend/src/data/"):
        self.data_path = data_path
        self._texas_counties = None
        self._texas_all_counties = None
        self._texas_mapping = None
        
    def load_texas_counties(self) -> List[Dict[str, Any]]:
        """Load Texas counties data"""
        if self._texas_counties is not None:
            return self._texas_counties
            
        try:
            # Try to load from JS file
            with open(f"{self.data_path}texasCounties.js", 'r') as f:
                content = f.read()
                
            # Parse JavaScript array/object
            # Remove JS export/import statements and extract data
            content = content.replace('export default', '').replace('const texasCounties =', '').strip()
            if content.endswith(';'):
                content = content[:-1]
                
            # Try to parse as JSON
            try:
                self._texas_counties = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create mock data
                logger.warning("Could not parse texasCounties.js, using mock data")
                self._texas_counties = self._create_mock_counties()
                
        except FileNotFoundError:
            logger.warning("texasCounties.js not found, using mock data")
            self._texas_counties = self._create_mock_counties()
            
        return self._texas_counties
    
    def load_texas_all_counties(self) -> List[Dict[str, Any]]:
        """Load all Texas counties data"""
        if self._texas_all_counties is not None:
            return self._texas_all_counties
            
        try:
            with open(f"{self.data_path}texasCountiesStatewide.js", 'r') as f:
                content = f.read()
                
            # Parse JavaScript array/object
            content = content.replace('export default', '').replace('const texasCountiesStatewide =', '').strip()
            if content.endswith(';'):
                content = content[:-1]
                
            try:
                self._texas_all_counties = json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Could not parse texasCountiesStatewide.js, using mock data")
                self._texas_all_counties = self._create_mock_all_counties()
                
        except FileNotFoundError:
            logger.warning("texasCountiesStatewide.js not found, using mock data")
            self._texas_all_counties = self._create_mock_all_counties()
            
        return self._texas_all_counties
    
    def load_texas_mapping(self) -> Dict[str, Any]:
        """Load Texas mapping data"""
        if self._texas_mapping is not None:
            return self._texas_mapping
            
        try:
            with open(f"{self.data_path}texasMapping.json", 'r') as f:
                self._texas_mapping = json.load(f)
        except FileNotFoundError:
            logger.warning("texasMapping.json not found, using mock data")
            self._texas_mapping = self._create_mock_mapping()
            
        return self._texas_mapping
    
    def _create_mock_counties(self) -> List[Dict[str, Any]]:
        """Create mock county data for development"""
        return [
            {"name": "Harris County", "fips": "48201", "population": 4731145},
            {"name": "Dallas County", "fips": "48113", "population": 2635516},
            {"name": "Tarrant County", "fips": "48439", "population": 2110640},
            {"name": "Bexar County", "fips": "48029", "population": 2009324},
            {"name": "Travis County", "fips": "48453", "population": 1290188},
            {"name": "Collin County", "fips": "48085", "population": 1056924},
            {"name": "Hidalgo County", "fips": "48215", "population": 868707},
            {"name": "El Paso County", "fips": "48141", "population": 868859},
            {"name": "Fort Bend County", "fips": "48157", "population": 822779},
            {"name": "Montgomery County", "fips": "48339", "population": 607391},
        ]
    
    def _create_mock_all_counties(self) -> List[Dict[str, Any]]:
        """Create mock data for all counties including smaller ones"""
        base_counties = self._create_mock_counties()
        additional_counties = [
            {"name": "Williamson County", "fips": "48491", "population": 590551},
            {"name": "Cameron County", "fips": "48061", "population": 423163},
            {"name": "Nueces County", "fips": "48355", "population": 362265},
            {"name": "Bell County", "fips": "48027", "population": 370647},
            {"name": "Galveston County", "fips": "48167", "population": 342139},
        ]
        return base_counties + additional_counties
    
    def _create_mock_mapping(self) -> Dict[str, Any]:
        """Create mock mapping data"""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"FIPS": "48201", "NAME": "Harris County"},
                    "geometry": {"type": "Polygon", "coordinates": [[[-95.9, 29.5], [-95.0, 29.5], [-95.0, 30.1], [-95.9, 30.1], [-95.9, 29.5]]]}
                },
                {
                    "type": "Feature", 
                    "properties": {"FIPS": "48113", "NAME": "Dallas County"},
                    "geometry": {"type": "Polygon", "coordinates": [[[-97.0, 32.6], [-96.4, 32.6], [-96.4, 33.0], [-97.0, 33.0], [-97.0, 32.6]]]}
                }
            ]
        }
    
    def get_county_dropdown_options(self) -> List[Dict[str, str]]:
        """Get dropdown options for county selection"""
        counties = self.load_texas_counties()
        return [{"label": county["name"], "value": county["fips"]} for county in counties]
    
    def get_all_county_dropdown_options(self) -> List[Dict[str, str]]:
        """Get dropdown options for all county selection"""
        counties = self.load_texas_all_counties()
        return [{"label": county["name"], "value": county["fips"]} for county in counties]
    
    def get_county_name_by_fips(self, fips: str) -> str:
        """Get county name by FIPS code"""
        counties = self.load_texas_all_counties()
        for county in counties:
            if county["fips"] == fips:
                return county["name"]
        return f"County {fips}"