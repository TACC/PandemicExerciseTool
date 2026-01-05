#!/usr/bin/env python3
"""
Simple test script to verify the Dash frontend functionality
"""

import requests
import time
import json

def test_backend_connection():
    """Test if Django backend is accessible"""
    try:
        response = requests.get("http://localhost:8000/api/reset")
        if response.status_code == 200:
            print("✓ Backend connection successful")
            return True
        else:
            print(f"✗ Backend returned status {response.status_code}")
            return False
    except requests.ConnectionError:
        print("✗ Cannot connect to backend at localhost:8000")
        return False

def test_simulation_api():
    """Test the simulation API endpoints"""
    try:
        # Test simulation creation
        params = {
            'disease_name': 'COVID-19',
            'R0': 2.5,
            'beta_scale': 1.0,
            'tau': 5.1,
            'kappa': 1.0,
            'gamma': 0.1,
            'chi': 0.5,
            'rho': 0.8,
            'nu': 0.01,
            'initial_infected': json.dumps([{'fips_id': '48201', 'cases': 100}]),
            'npis': json.dumps([]),
            'vaccine_effectiveness': 0.85,
            'vaccine_adherence': 0.70,
            'vaccine_stockpile': 1000000,
            'vaccine_wastage_factor': 0.1,
            'vaccine_pro_rata': 'proportional',
            'antiviral_effectiveness': 0.75,
            'antiviral_stockpile': 500000,
            'antiviral_wastage_factor': 0.05,
        }
        
        response = requests.post("http://localhost:8000/api/pet/", json=params)
        if response.status_code == 201:
            sim_id = response.json().get('id')
            print(f"✓ Simulation created with ID: {sim_id}")
            
            # Test simulation run
            run_response = requests.get(f"http://localhost:8000/api/pet/{sim_id}/run")
            if run_response.status_code == 202:
                task_id = run_response.json().get('task_id')
                print(f"✓ Simulation started with task ID: {task_id}")
                
                # Wait a moment and test output retrieval
                time.sleep(2)
                output_response = requests.get("http://localhost:8000/api/output/0")
                if output_response.status_code in [200, 404]:  # 404 is expected if data not ready
                    print("✓ Output endpoint accessible")
                    
                    # Clean up
                    requests.get(f"http://localhost:8000/api/delete/{task_id}")
                    print("✓ Simulation cleanup completed")
                    return True
                else:
                    print(f"✗ Output endpoint returned {output_response.status_code}")
            else:
                print(f"✗ Simulation run failed with status {run_response.status_code}")
        else:
            print(f"✗ Simulation creation failed with status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Simulation API test failed: {e}")
    
    return False

def test_data_loading():
    """Test data loading functionality"""
    try:
        from data_loader import DataLoader
        loader = DataLoader()
        
        counties = loader.load_texas_counties()
        print(f"✓ Loaded {len(counties)} Texas counties")
        
        options = loader.get_county_dropdown_options()
        print(f"✓ Generated {len(options)} dropdown options")
        
        return True
    except Exception as e:
        print(f"✗ Data loading test failed: {e}")
        return False

def test_visualization():
    """Test visualization generation"""
    try:
        from data_loader import DataLoader
        from visualization import VisualizationGenerator
        
        loader = DataLoader()
        viz = VisualizationGenerator(loader)
        
        # Test with empty data
        empty_map = viz.create_choropleth_map([], 0, 'percent')
        print("✓ Empty map generation successful")
        
        empty_chart = viz.create_line_chart([])
        print("✓ Empty chart generation successful")
        
        empty_table = viz.create_summary_table([], 0, 'percent')
        print("✓ Empty table generation successful")
        
        return True
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Pandemic Dash Frontend Components\n")
    
    tests = [
        ("Backend Connection", test_backend_connection),
        ("Data Loading", test_data_loading),
        ("Visualization", test_visualization),
        ("Simulation API", test_simulation_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The Dash frontend is ready to use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")