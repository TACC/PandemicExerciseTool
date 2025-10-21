import dash
from dash import dcc, html, Input, Output, State, callback, ctx, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import json
import time
from datetime import datetime
import logging
from threading import Timer
import base64

from api_client import PandemicAPIClient
from data_loader import DataLoader
from visualization import VisualizationGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "epiENGAGE - Interactive Outbreak Simulator"

# Initialize components
api_client = PandemicAPIClient()
data_loader = DataLoader()
viz_generator = VisualizationGenerator(data_loader)

# Define layout functions first
def create_home_page():
    return dbc.Row([
        # Left Panel - Controls
        dbc.Col([
            html.Div([
                # Set Scenario Section
                dbc.Card([
                    dbc.CardHeader("Set Scenario"),
                    dbc.CardBody([
                        html.H6("Disease Parameters"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Disease Name"),
                                dbc.Input(id="disease-name", value="COVID-19", type="text")
                            ], width=12),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Reproduction Number (R₀)"),
                                dbc.Input(id="reproduction-number", value=2.5, type="number", step=0.1)
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Beta Scale"),
                                dbc.Input(id="beta-scale", value=1.0, type="number", step=0.1)
                            ], width=6),
                        ], className="mt-2"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Tau"),
                                dbc.Input(id="tau", value=5.1, type="number", step=0.1)
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Kappa"),
                                dbc.Input(id="kappa", value=1.0, type="number", step=0.1)
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Gamma"),
                                dbc.Input(id="gamma", value=0.1, type="number", step=0.01)
                            ], width=4),
                        ], className="mt-2"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Chi"),
                                dbc.Input(id="chi", value=0.5, type="number", step=0.1)
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Rho"),
                                dbc.Input(id="rho", value=0.8, type="number", step=0.1)
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Nu"),
                                dbc.Input(id="nu", value=0.01, type="number", step=0.001)
                            ], width=4),
                        ], className="mt-2"),
                        
                        html.Hr(),
                        
                        html.H6("Initial Cases"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Select Counties"),
                                dcc.Dropdown(
                                    id="initial-counties",
                                    options=data_loader.get_county_dropdown_options(),
                                    multi=True,
                                    placeholder="Select counties for initial cases"
                                )
                            ], width=12),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Cases per County"),
                                dbc.Input(id="initial-cases-count", value=100, type="number", min=1)
                            ], width=12),
                        ], className="mt-2"),
                        
                        html.Hr(),
                        
                        dbc.Button("Save Scenario", id="save-scenario-btn", color="primary", className="w-100")
                    ])
                ], className="mb-3"),
                
                # Interventions Section
                dbc.Card([
                    dbc.CardHeader("Interventions"),
                    dbc.CardBody([
                        html.H6("Non-Pharmaceutical Interventions"),
                        dbc.Checklist(
                            id="npi-checklist",
                            options=[
                                {"label": "School Closures", "value": "school_closures"},
                                {"label": "Workplace Closures", "value": "workplace_closures"},
                                {"label": "Social Distancing", "value": "social_distancing"},
                                {"label": "Travel Restrictions", "value": "travel_restrictions"}
                            ],
                            value=[]
                        ),
                        
                        html.Hr(),
                        
                        html.H6("Vaccines"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Effectiveness (%)"),
                                dbc.Input(id="vaccine-effectiveness", value=85, type="number", min=0, max=100)
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Adherence (%)"),
                                dbc.Input(id="vaccine-adherence", value=70, type="number", min=0, max=100)
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Stockpile"),
                                dbc.Input(id="vaccine-stockpile", value=1000000, type="number", min=0)
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Wastage Factor"),
                                dbc.Input(id="vaccine-wastage", value=0.1, type="number", step=0.01, min=0, max=1)
                            ], width=6),
                        ], className="mt-2"),
                        
                        html.Hr(),
                        
                        html.H6("Antivirals"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Effectiveness (%)"),
                                dbc.Input(id="antiviral-effectiveness", value=75, type="number", min=0, max=100)
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Stockpile"),
                                dbc.Input(id="antiviral-stockpile", value=500000, type="number", min=0)
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Wastage Factor"),
                                dbc.Input(id="antiviral-wastage", value=0.05, type="number", step=0.01, min=0, max=1)
                            ], width=12),
                        ], className="mt-2"),
                    ])
                ], className="mb-3"),
                
                # Current Parameters Display
                dbc.Card([
                    dbc.CardHeader("Current Parameters"),
                    dbc.CardBody(id="parameters-display", children=[
                        html.P("No parameters set yet.", className="text-muted")
                    ])
                ])
            ])
        ], width=2),
        
        # Middle Panel - Map and Chart
        dbc.Col([
            # View toggle
            dbc.Card([
                dbc.CardBody([
                    html.H6("Show values as:"),
                    dbc.RadioItems(
                        id="view-toggle",
                        options=[
                            {"label": "Percentage", "value": "percent"},
                            {"label": "Count", "value": "count"}
                        ],
                        value="percent",
                        inline=True
                    )
                ])
            ], className="mb-3"),
            
            # Map
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id="spread-map",
                        style={'height': '400px'},
                        config={'displayModeBar': False}
                    )
                ])
            ], className="mb-3"),
            
            # Line Chart
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id="line-chart",
                        style={'height': '300px'},
                        config={'displayModeBar': False}
                    )
                ])
            ])
        ], width=7),
        
        # Right Panel - Table
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H6("County Data", className="mb-0")
                ]),
                dbc.CardBody([
                    html.Div(id="spread-table")
                ])
            ])
        ], width=3),
        
        # Footer - Controls
        dbc.Row([
            dbc.Col([
                html.Div([
                    # Play/Pause Button
                    dbc.Button(
                        "Play", 
                        id="play-pause-btn", 
                        color="success", 
                        size="lg",
                        disabled=True,
                        className="me-3"
                    ),
                    
                    # Timeline Slider
                    html.Div([
                        dcc.Slider(
                            id="timeline-slider",
                            min=0,
                            max=30,
                            value=0,
                            marks={i: str(i) for i in range(0, 31, 5)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            disabled=True
                        )
                    ], style={'width': '70%', 'display': 'inline-block'})
                ], className="d-flex align-items-center justify-content-center")
            ], width=12)
        ], className="mt-4 mb-2"),
    ])

# User Guide page layout
def create_user_guide_page():
    return dbc.Container([
        html.H2("User Guide", className="mb-4"),
        dbc.Tabs([
            dbc.Tab(label="Instructions", tab_id="instructions"),
            dbc.Tab(label="Model Information", tab_id="model-info"),
        ], id="userguide-tabs", active_tab="instructions"),
        html.Div(id="userguide-content", children=render_userguide_content("instructions"), className="mt-3")
    ])

def render_userguide_content(active_tab):
    if active_tab == "model-info":
        return dbc.Card([
            dbc.CardBody([
                html.H4("SEATIRD Epidemic Model"),
                html.P("The pandemic simulator uses a SEATIRD compartmental model to simulate disease spread:"),
                html.Ul([
                    html.Li(html.Strong("S - Susceptible: ") + "Individuals who can become infected"),
                    html.Li(html.Strong("E - Exposed: ") + "Individuals who have been exposed but are not yet infectious"),
                    html.Li(html.Strong("A - Asymptomatic: ") + "Infectious individuals without symptoms"),
                    html.Li(html.Strong("T - Treatable: ") + "Symptomatic individuals who can receive treatment"),
                    html.Li(html.Strong("I - Infected: ") + "Symptomatic infectious individuals"),
                    html.Li(html.Strong("R - Recovered: ") + "Individuals who have recovered and are immune"),
                    html.Li(html.Strong("D - Deceased: ") + "Individuals who have died from the disease"),
                ]),
                html.Hr(),
                html.H5("Model Parameters"),
                html.Ul([
                    html.Li(html.Strong("R₀ (Basic Reproduction Number): ") + "Average number of secondary infections caused by one infected individual"),
                    html.Li(html.Strong("Beta Scale: ") + "Transmission rate scaling factor"),
                    html.Li(html.Strong("Tau: ") + "Incubation period (days)"),
                    html.Li(html.Strong("Kappa: ") + "Rate of progression from exposed to infectious"),
                    html.Li(html.Strong("Gamma: ") + "Recovery rate"),
                    html.Li(html.Strong("Chi: ") + "Proportion developing symptoms"),
                    html.Li(html.Strong("Rho: ") + "Treatment seeking rate"),
                    html.Li(html.Strong("Nu: ") + "Case fatality rate"),
                ]),
            ])
        ])
    
    # Default to instructions
    return dbc.Card([
        dbc.CardBody([
            html.H4("How to Use the Pandemic Simulator"),
            html.Ol([
                html.Li([
                    html.Strong("Set Disease Parameters: "),
                    "Configure the disease characteristics including reproduction number, incubation period, and other epidemiological parameters."
                ]),
                html.Li([
                    html.Strong("Select Initial Cases: "),
                    "Choose which Texas counties will have initial cases and specify the number of cases per county."
                ]),
                html.Li([
                    html.Strong("Configure Interventions: "),
                    "Set up non-pharmaceutical interventions (like school closures), vaccine parameters, and antiviral treatments."
                ]),
                html.Li([
                    html.Strong("Save Scenario: "),
                    "Click 'Save Scenario' to prepare your simulation with the configured parameters."
                ]),
                html.Li([
                    html.Strong("Run Simulation: "),
                    "Click the 'Play' button to start the simulation. You can pause it at any time."
                ]),
                html.Li([
                    html.Strong("View Results: "),
                    "Monitor the outbreak progression through the map, epidemic curve, and county data table. Toggle between count and percentage views."
                ]),
                html.Li([
                    html.Strong("Timeline Navigation: "),
                    "Use the timeline slider to review results from different days of the simulation."
                ]),
            ]),
            html.Hr(),
            html.H5("Interface Elements"),
            html.Ul([
                html.Li(html.Strong("Left Panel: ") + "Disease parameters, initial cases, and intervention settings"),
                html.Li(html.Strong("Middle Panel: ") + "Geographic map showing disease spread and epidemic curve chart"),
                html.Li(html.Strong("Right Panel: ") + "County-by-county summary table"),
                html.Li(html.Strong("Bottom Panel: ") + "Simulation controls and timeline slider"),
            ]),
        ])
    ])

# App layout
app.layout = dbc.Container([
    dcc.Store(id='simulation-state', data={'is_running': False, 'current_index': 0, 'task_id': None, 'simulation_id': None}),
    dcc.Store(id='event-data', data=[]),
    dcc.Store(id='simulation-parameters', data={}),
    dcc.Interval(id='simulation-interval', interval=1000, n_intervals=0, disabled=True),
    
    # Header
    dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Img(src="/assets/epiengage_logo_darkblue.jpg", height="60px", className="me-3"),
                    dbc.NavbarBrand("epiENGAGE", className="fw-bold text-white")
                ], width="auto"),
                dbc.Col([
                    dbc.Nav([
                        dbc.NavLink("Home", href="#", id="nav-home", active=True, className="text-white mx-2"),
                        dbc.NavLink("User Guide", href="#", id="nav-userguide", active=False, className="text-white mx-2"),
                    ], navbar=True, className="mx-auto")
                ], width=True),
                dbc.Col([
                    html.Span("Interactive Outbreak Simulator", className="text-white")
                ], width="auto")
            ], align="center", className="w-100")
        ], fluid=True)
    ], color="#102c41", dark=True, fixed="top", className="mb-4"),
    
    # Main content area
    html.Div(id="main-content", children=create_home_page(), style={"margin-top": "80px"}),
    
], fluid=True)

# User Guide content callback
@callback(
    Output('userguide-content', 'children'),
    Input('userguide-tabs', 'active_tab'),
    prevent_initial_call=True
)
def update_userguide_content(active_tab):
    return render_userguide_content(active_tab or "instructions")

# Navigation callback
@callback(
    Output('main-content', 'children'),
    [Input('nav-home', 'n_clicks'),
     Input('nav-userguide', 'n_clicks')],
    prevent_initial_call=True
)
def navigate_pages(home_clicks, userguide_clicks):
    if ctx.triggered_id == 'nav-userguide':
        return create_user_guide_page()
    else:
        return create_home_page()

# Scenario saving callback
@callback(
    [Output('parameters-display', 'children'),
     Output('play-pause-btn', 'disabled'),
     Output('save-scenario-btn', 'children'),
     Output('simulation-parameters', 'data')],
    Input('save-scenario-btn', 'n_clicks'),
    [State('disease-name', 'value'),
     State('reproduction-number', 'value'),
     State('beta-scale', 'value'),
     State('tau', 'value'),
     State('kappa', 'value'),
     State('gamma', 'value'),
     State('chi', 'value'),
     State('rho', 'value'),
     State('nu', 'value'),
     State('initial-counties', 'value'),
     State('initial-cases-count', 'value'),
     State('npi-checklist', 'value'),
     State('vaccine-effectiveness', 'value'),
     State('vaccine-adherence', 'value'),
     State('vaccine-stockpile', 'value'),
     State('vaccine-wastage', 'value'),
     State('antiviral-effectiveness', 'value'),
     State('antiviral-stockpile', 'value'),
     State('antiviral-wastage', 'value')],
    prevent_initial_call=True
)
def save_scenario(n_clicks, disease_name, r0, beta_scale, tau, kappa, gamma, chi, rho, nu,
                 initial_counties, initial_cases, npis, vaccine_eff, vaccine_adh, vaccine_stock, vaccine_waste,
                 antiviral_eff, antiviral_stock, antiviral_waste):
    if n_clicks:
        # Save parameters for simulation
        parameters = {
            'disease_name': disease_name,
            'reproduction_number': r0,
            'beta_scale': beta_scale,
            'tau': tau,
            'kappa': kappa,
            'gamma': gamma,
            'chi': chi,
            'rho': rho,
            'nu': nu,
            'initial_counties': initial_counties,
            'initial_cases_count': initial_cases,
            'npi_checklist': npis,
            'vaccine_effectiveness': vaccine_eff,
            'vaccine_adherence': vaccine_adh,
            'vaccine_stockpile': vaccine_stock,
            'vaccine_wastage': vaccine_waste,
            'antiviral_effectiveness': antiviral_eff,
            'antiviral_stockpile': antiviral_stock,
            'antiviral_wastage': antiviral_waste,
        }
        
        # Create parameters display
        county_names = []
        if initial_counties:
            for fips in initial_counties:
                county_names.append(data_loader.get_county_name_by_fips(fips))
        
        params_display = [
            html.H6("Disease Parameters"),
            html.P(f"Disease: {disease_name}"),
            html.P(f"R₀: {r0}"),
            html.P(f"Beta Scale: {beta_scale}"),
            html.Hr(),
            html.H6("Initial Cases"),
            html.P(f"Counties: {', '.join(county_names) if county_names else 'None'}"),
            html.P(f"Cases per County: {initial_cases}"),
            html.Hr(),
            html.H6("Interventions"),
            html.P(f"NPIs: {', '.join(npis) if npis else 'None'}"),
            html.P(f"Vaccine Effectiveness: {vaccine_eff}%"),
            html.P(f"Antiviral Effectiveness: {antiviral_eff}%"),
        ]
        
        return params_display, False, "Scenario Saved ✓", parameters
    
    return dash.no_update, True, "Save Scenario", dash.no_update

# Play/Pause simulation callback
@callback(
    [Output('simulation-state', 'data'),
     Output('play-pause-btn', 'children'),
     Output('play-pause-btn', 'color'),
     Output('simulation-interval', 'disabled')],
    Input('play-pause-btn', 'n_clicks'),
    [State('simulation-state', 'data'),
     State('simulation-parameters', 'data')],
    prevent_initial_call=True
)
def toggle_simulation(n_clicks, sim_state, sim_params):
    if n_clicks:
        is_running = sim_state.get('is_running', False)
        
        if not is_running:
            # Start simulation - first create and run simulation via API
            if sim_params:
                # Format parameters for API
                api_params = api_client.format_simulation_parameters(sim_params)
                
                # Create simulation
                simulation_id = api_client.create_simulation(api_params)
                if simulation_id:
                    # Start simulation
                    task_id = api_client.run_simulation(simulation_id)
                    if task_id:
                        new_state = {
                            **sim_state, 
                            'is_running': True, 
                            'current_index': 0,
                            'simulation_id': simulation_id,
                            'task_id': task_id
                        }
                        return new_state, "Pause", "warning", False
            
            # If simulation start failed, stay in play state
            return sim_state, "Play", "success", True
        else:
            # Pause simulation - stop the task
            task_id = sim_state.get('task_id')
            if task_id:
                api_client.stop_simulation(task_id)
            
            new_state = {**sim_state, 'is_running': False}
            return new_state, "Play", "success", True
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Map visualization callback
@callback(
    Output('spread-map', 'figure'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value')],
    prevent_initial_call=False
)
def update_map(event_data, timeline_value, view_type):
    try:
        return viz_generator.create_choropleth_map(event_data or [], timeline_value or 0, view_type or 'percent')
    except Exception as e:
        logger.error(f"Error updating map: {e}")
        return viz_generator.create_choropleth_map([], 0, 'percent')

# Line chart callback
@callback(
    Output('line-chart', 'figure'),
    Input('event-data', 'data'),
    prevent_initial_call=False
)
def update_line_chart(event_data):
    try:
        return viz_generator.create_line_chart(event_data or [])
    except Exception as e:
        logger.error(f"Error updating line chart: {e}")
        return viz_generator.create_line_chart([])

# Table callback
@callback(
    Output('spread-table', 'children'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value')],
    prevent_initial_call=False
)
def update_table(event_data, timeline_value, view_type):
    try:
        if not event_data or timeline_value is None or timeline_value >= len(event_data):
            return html.P("No data available", className="text-muted")
        
        df = viz_generator.create_summary_table(event_data, timeline_value, view_type or 'percent')
        
        if df.empty:
            return html.P("No county data available", className="text-muted")
        
        return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size='sm')
    except Exception as e:
        logger.error(f"Error updating table: {e}")
        return html.P("Error loading data", className="text-muted")

# Timeline slider callback
@callback(
    Output('timeline-slider', 'value'),
    Input('simulation-state', 'data'),
    State('event-data', 'data'),
    prevent_initial_call=True
)
def update_timeline(sim_state, event_data):
    if sim_state.get('is_running', False) and event_data:
        return len(event_data) - 1
    return dash.no_update

# Simulation data fetching
@callback(
    [Output('event-data', 'data'),
     Output('timeline-slider', 'max'),
     Output('timeline-slider', 'disabled'),
     Output('simulation-state', 'data', allow_duplicate=True)],
    Input('simulation-interval', 'n_intervals'),
    [State('simulation-state', 'data'),
     State('event-data', 'data')],
    prevent_initial_call=True
)
def fetch_simulation_data(n_intervals, sim_state, event_data):
    if sim_state.get('is_running', False):
        current_day = len(event_data)
        
        # Fetch data from API
        api_data = api_client.get_simulation_output(current_day)
        
        if api_data:
            # Process API response to match expected format
            day_data = {
                'day': api_data.get('day', current_day),
                'counties': [],
                'totalSusceptible': 0,
                'totalExposed': 0,
                'totalAsymptomaticCount': 0,
                'totalTreatableCount': 0,
                'totalInfectedCount': 0,
                'totalRecoveredCount': 0,
                'totalDeceased': 0
            }
            
            # Extract county data
            if 'data' in api_data:
                for county_key, county_data in api_data['data'].items():
                    fips_id = county_data.get('fips_id', '')
                    compartments = county_data.get('compartment_summary', {})
                    compartments_percent = county_data.get('compartment_summary_percent', {})
                    
                    county_info = {
                        'fips': fips_id,
                        'infected': compartments.get('I', 0),
                        'deceased': compartments.get('D', 0),
                        'infectedPercent': compartments_percent.get('I', 0),
                        'deceasedPercent': compartments_percent.get('D', 0)
                    }
                    day_data['counties'].append(county_info)
            
            # Extract total summary
            if 'total_summary' in api_data:
                totals = api_data['total_summary']
                day_data.update({
                    'totalSusceptible': totals.get('S', 0),
                    'totalExposed': totals.get('E', 0),
                    'totalAsymptomaticCount': totals.get('A', 0),
                    'totalTreatableCount': totals.get('T', 0),
                    'totalInfectedCount': totals.get('I', 0),
                    'totalRecoveredCount': totals.get('R', 0),
                    'totalDeceased': totals.get('D', 0)
                })
            
            updated_event_data = event_data + [day_data]
            updated_sim_state = {**sim_state, 'current_index': len(updated_event_data) - 1}
            
            return updated_event_data, len(updated_event_data), False, updated_sim_state
        
        # If no new data available yet, keep current state
        return event_data, max(30, len(event_data)), False, sim_state
    
    return event_data, max(30, len(event_data)), len(event_data) == 0, sim_state

# Expose server for Gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host='0.0.0.0')

