#!/usr/bin/env python3
"""
Quick test to verify the Dash app works without errors
"""

def test_app_creation():
    try:
        import dash
        from dash import dcc, html, Input, Output, State, callback, ctx
        import dash_bootstrap_components as dbc
        print("✓ Dash imports successful")
        
        from api_client import PandemicAPIClient
        from data_loader import DataLoader
        from visualization import VisualizationGenerator
        print("✓ Custom imports successful")
        
        # Initialize components
        api_client = PandemicAPIClient()
        data_loader = DataLoader()
        viz_generator = VisualizationGenerator(data_loader)
        print("✓ Components initialized")
        
        # Test data loading
        counties = data_loader.get_county_dropdown_options()
        print(f"✓ Loaded {len(counties)} county options")
        
        # Test visualization creation
        empty_map = viz_generator.create_choropleth_map([], 0, 'percent')
        print("✓ Map creation works")
        
        empty_chart = viz_generator.create_line_chart([])
        print("✓ Chart creation works")
        
        empty_table = viz_generator.create_summary_table([], 0, 'percent')
        print("✓ Table creation works")
        
        print("\n🎉 All tests passed! The app should work correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_app_creation()