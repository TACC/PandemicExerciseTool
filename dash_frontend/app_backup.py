import dash
from dash import dcc, html, Input, Output, State, callback, ctx, ALL, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import requests
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app with external CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "epiENGAGE - Interactive Outbreak Simulator"
app.config.suppress_callback_exceptions = True

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# Load Texas counties data exactly like React
def load_texas_counties():
    """Load Texas counties exactly like the React version"""
    try:
        # Read the JS file
        with open('../frontend/src/data/texasCounties.js', 'r') as f:
            content = f.read()
        
        # Extract just the county names manually since JSON parsing fails
        lines = content.split('\n')
        counties = []
        for line in lines:
            line = line.strip()
            if line.startswith("'") and line.endswith("',"):
                county = line[1:-2]  # Remove quotes and comma
                counties.append(county)
            elif line.startswith("'") and line.endswith("'"):
                county = line[1:-1]  # Remove quotes only
                counties.append(county)
        
        return counties if counties else [
            'Anderson', 'Andrews', 'Angelina', 'Aransas', 'Archer', 'Armstrong',
            'Atascosa', 'Austin', 'Bailey', 'Bandera', 'Bastrop', 'Baylor',
            'Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis', 'Collin'
        ]
    except Exception as e:
        logger.warning(f"Could not load Texas counties: {e}")
        # Use fallback data
        return [
            'Anderson', 'Andrews', 'Angelina', 'Aransas', 'Archer', 'Armstrong',
            'Atascosa', 'Austin', 'Bailey', 'Bandera', 'Bastrop', 'Baylor',
            'Harris', 'Dallas', 'Tarrant', 'Bexar', 'Travis', 'Collin'
        ]

# Load Texas counties
texas_counties = load_texas_counties()

# App Layout - Exact match to React structure
app.layout = html.Div([
    # Stores for state management (like React useState)
    dcc.Store(id='simulation-state', data={'isRunning': False, 'currentIndex': 0, 'taskId': None, 'id': None}),
    dcc.Store(id='event-data', data=[]),
    dcc.Store(id='view-type', data='percent'),
    dcc.Store(id='last-sorted', data={'category': 'county', 'order': 'asc'}),
    dcc.Store(id='has-set-scenario', data=False),
    dcc.Store(id='has-set-cases', data=False),
    dcc.Interval(id='simulation-interval', interval=1000, disabled=True),
    
    # Header - Exact match to React Header component
    html.Nav([
        html.Div([
            html.Div([
                html.Div([
                    html.Img(
                        src='/assets/epiengage_logo_darkblue.jpg',
                        style={'width': '60px', 'height': '60px'},
                        className='align-top header-logo'
                    ),
                    html.Span('epiENGAGE', className='header-name', style={
                        'color': 'white',
                        'fontSize': '24px',
                        'fontWeight': 'bold',
                        'marginLeft': '10px'
                    })
                ], style={'display': 'flex', 'alignItems': 'center'}),
                
                html.Div([
                    html.Ul([
                        html.Li([
                            html.A('Home', 
                                id='nav-home',
                                className='tab-button active',
                                style={'cursor': 'pointer', 'color': 'white', 'textDecoration': 'none', 'padding': '10px 20px'})
                        ]),
                        html.Li([
                            html.A('User Guide',
                                id='nav-userguide', 
                                className='tab-button',
                                style={'cursor': 'pointer', 'color': 'white', 'textDecoration': 'none', 'padding': '10px 20px'})
                        ])
                    ], style={'listStyle': 'none', 'display': 'flex', 'margin': '0', 'padding': '0'})
                ], style={'flex': '1', 'textAlign': 'center'}),
                
                html.Div([
                    html.Span('Interactive Outbreak Simulator', style={'color': 'white'})
                ])
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'width': '100%',
                'padding': '0 20px'
            })
        ], className='container-fluid')
    ], style={
        'backgroundColor': '#102c41',
        'position': 'fixed',
        'top': '0',
        'width': '100%',
        'zIndex': '1000',
        'padding': '10px 0'
    }),
    
    # Main content area
    html.Div(id='main-content', style={'marginTop': '80px'})
])

# Home page layout - Exact match to React Home component
def create_home_layout():
    return html.Div([
        html.Div([
            # Left Panel - SetScenario, Interventions, DisplayedParameters
            html.Div([
                html.Div([
                    # Set Scenario dropdown (like React SetScenario component)
                    html.Div([
                        html.Button([
                            html.Span('Set Scenario', className='dropdown-text'),
                            html.Span('▾', className='dropdown-arrow')
                        ], 
                        id='set-scenario-btn',
                        className='parameters-button',
                        style={
                            'width': '100%',
                            'padding': '10px',
                            'backgroundColor': '#f8f9fa',
                            'border': '1px solid #dee2e6',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'display': 'flex',
                            'justifyContent': 'space-between',
                            'alignItems': 'center'
                        }),
                        
                        # Dropdown menu
                        html.Div([
                            html.Button('Disease Parameters', 
                                id='disease-params-btn',
                                className='dropdown-items',
                                style={
                                    'width': '100%',
                                    'padding': '8px 12px',
                                    'border': 'none',
                                    'backgroundColor': 'white',
                                    'textAlign': 'left',
                                    'cursor': 'pointer'
                                }),
                            html.Button('Initial Cases',
                                id='initial-cases-btn', 
                                className='dropdown-items',
                                style={
                                    'width': '100%',
                                    'padding': '8px 12px',
                                    'border': 'none',
                                    'backgroundColor': 'white',
                                    'textAlign': 'left',
                                    'cursor': 'pointer'
                                })
                        ],
                        id='scenario-dropdown',
                        style={
                            'display': 'none',
                            'position': 'absolute',
                            'top': '100%',
                            'left': '0',
                            'right': '0',
                            'backgroundColor': 'white',
                            'border': '1px solid #dee2e6',
                            'borderTop': 'none',
                            'borderRadius': '0 0 4px 4px',
                            'zIndex': 1000
                        })
                    ], style={'position': 'relative', 'marginBottom': '10px'}),
                    
                    # Interventions section
                    html.Div([
                        html.H6('Interventions', style={'marginBottom': '10px'}),
                        html.H6('Non-Pharmaceutical Interventions', style={'fontSize': '14px', 'marginBottom': '5px'}),
                        dcc.Checklist(
                            id='npi-checklist',
                            options=[
                                {'label': ' School Closures', 'value': 'school_closures'},
                                {'label': ' Workplace Closures', 'value': 'workplace_closures'},
                                {'label': ' Social Distancing', 'value': 'social_distancing'},
                                {'label': ' Travel Restrictions', 'value': 'travel_restrictions'}
                            ],
                            value=[],
                            style={'marginBottom': '15px'}
                        ),
                        
                        html.H6('Vaccines', style={'fontSize': '14px', 'marginBottom': '5px'}),
                        html.Div([
                            html.Label('Effectiveness (%)', style={'fontSize': '12px'}),
                            dcc.Input(id='vaccine-effectiveness', type='number', value=85, min=0, max=100,
                                style={'width': '100%', 'marginBottom': '5px'})
                        ]),
                        html.Div([
                            html.Label('Adherence (%)', style={'fontSize': '12px'}),
                            dcc.Input(id='vaccine-adherence', type='number', value=70, min=0, max=100,
                                style={'width': '100%', 'marginBottom': '5px'})
                        ]),
                        html.Div([
                            html.Label('Stockpile', style={'fontSize': '12px'}),
                            dcc.Input(id='vaccine-stockpile', type='number', value=1000000, min=0,
                                style={'width': '100%', 'marginBottom': '10px'})
                        ]),
                        
                        html.H6('Antivirals', style={'fontSize': '14px', 'marginBottom': '5px'}),
                        html.Div([
                            html.Label('Effectiveness (%)', style={'fontSize': '12px'}),
                            dcc.Input(id='antiviral-effectiveness', type='number', value=75, min=0, max=100,
                                style={'width': '100%', 'marginBottom': '5px'})
                        ]),
                        html.Div([
                            html.Label('Stockpile', style={'fontSize': '12px'}),
                            dcc.Input(id='antiviral-stockpile', type='number', value=500000, min=0,
                                style={'width': '100%'})
                        ])
                    ], style={
                        'border': '1px solid #dee2e6',
                        'borderRadius': '4px',
                        'padding': '15px',
                        'marginBottom': '10px',
                        'backgroundColor': 'white'
                    }),
                    
                    # DisplayedParameters section
                    html.Div([
                        html.H6('Current Parameters', style={'marginBottom': '10px'}),
                        html.Div(id='displayed-parameters', children=[
                            html.P('No parameters set yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})
                        ])
                    ], style={
                        'border': '1px solid #dee2e6',
                        'borderRadius': '4px',
                        'padding': '15px',
                        'backgroundColor': 'white'
                    })
                ], className='left-panel')
            ], className='col-lg-2'),
            
            # Middle Panel - Map and Chart
            html.Div([
                # View toggle (count/percent)
                html.Div([
                    html.H6('Show values as:', style={'marginBottom': '10px'}),
                    dcc.RadioItems(
                        id='view-toggle',
                        options=[
                            {'label': ' Percentage', 'value': 'percent'},
                            {'label': ' Count', 'value': 'count'}
                        ],
                        value='percent',
                        inline=True,
                        style={'marginBottom': '15px'}
                    )
                ], className='top-middle-panel'),
                
                # Map and Chart container
                html.Div([
                    # Map
                    dcc.Graph(
                        id='spread-map',
                        style={'height': '400px', 'marginBottom': '10px'},
                        config={'displayModeBar': False}
                    ),
                    
                    # Line Chart
                    dcc.Graph(
                        id='line-chart',
                        style={'height': '300px'},
                        config={'displayModeBar': False}
                    )
                ], className='map-and-chart-container')
            ], className='col-lg-7'),
            
            # Right Panel - Table
            html.Div([
                html.Div([
                    html.H6('County Data', style={'marginBottom': '15px'}),
                    html.Div(id='spread-table')
                ], className='right-panel')
            ], className='col-lg-3'),
            
            # Footer - Play/Pause and Timeline
            html.Div([
                html.Div([
                    # Play/Pause Button
                    html.Button(
                        'Play',
                        id='play-pause-btn',
                        disabled=True,
                        style={
                            'padding': '10px 30px',
                            'fontSize': '16px',
                            'backgroundColor': '#28a745',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'marginRight': '20px'
                        }
                    ),
                    
                    # Timeline Slider
                    html.Div([
                        dcc.Slider(
                            id='timeline-slider',
                            min=0,
                            max=30,
                            value=0,
                            marks={i: str(i) for i in range(0, 31, 5)},
                            tooltip={'placement': 'bottom', 'always_visible': True},
                            disabled=True
                        )
                    ], style={'width': '70%', 'display': 'inline-block'})
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'padding': '20px'
                })
            ], style={'marginTop': '20px'})
        ], className='row')
    ])

# User Guide layout
def create_userguide_layout():
    return html.Div([
        html.H2('User Guide', style={'marginBottom': '20px'}),
        dcc.Tabs(id='userguide-tabs', value='instructions', children=[
            dcc.Tab(label='Instructions', value='instructions'),
            dcc.Tab(label='Model Information', value='model-info')
        ]),
        html.Div(id='userguide-content', style={'marginTop': '20px'})
    ])

# User Guide layout
def create_userguide_layout():
    return html.Div([
        html.Div([
            html.H2('User Guide', style={'marginBottom': '20px', 'color': '#102c41'}),
            html.Div(id='userguide-content', children=[
                html.H4('How to Use the Pandemic Simulator'),
                html.Ol([
                    html.Li([html.B('Set Disease Parameters: '), 'Configure the disease characteristics including reproduction number, incubation period, and other epidemiological parameters.']),
                    html.Li([html.B('Select Initial Cases: '), 'Choose which Texas counties will have initial cases and specify the number of cases per county.']),
                    html.Li([html.B('Configure Interventions: '), 'Set up non-pharmaceutical interventions (like school closures), vaccine parameters, and antiviral treatments.']),
                    html.Li([html.B('Save Scenario: '), 'Click "Save Scenario" to prepare your simulation with the configured parameters.']),
                    html.Li([html.B('Run Simulation: '), 'Click the "Play" button to start the simulation. You can pause it at any time.']),
                    html.Li([html.B('View Results: '), 'Monitor the outbreak progression through the map, epidemic curve, and county data table. Toggle between count and percentage views.']),
                    html.Li([html.B('Timeline Navigation: '), 'Use the timeline slider to review results from different days of the simulation.'])
                ]),
                html.Hr(),
                html.H5('SEATIRD Model'),
                html.P('The pandemic simulator uses a SEATIRD compartmental model:'),
                html.Ul([
                    html.Li([html.B('S - Susceptible: '), 'Individuals who can become infected']),
                    html.Li([html.B('E - Exposed: '), 'Individuals who have been exposed but are not yet infectious']),
                    html.Li([html.B('A - Asymptomatic: '), 'Infectious individuals without symptoms']),
                    html.Li([html.B('T - Treatable: '), 'Symptomatic individuals who can receive treatment']),
                    html.Li([html.B('I - Infected: '), 'Symptomatic infectious individuals']),
                    html.Li([html.B('R - Recovered: '), 'Individuals who have recovered and are immune']),
                    html.Li([html.B('D - Deceased: '), 'Individuals who have died from the disease'])
                ]),
                html.Hr(),
                html.H5('Interface Elements'),
                html.Ul([
                    html.Li([html.B('Left Panel: '), 'Disease parameters, initial cases, and intervention settings']),
                    html.Li([html.B('Middle Panel: '), 'Geographic map showing disease spread and epidemic curve chart']),
                    html.Li([html.B('Right Panel: '), 'County-by-county summary table']),
                    html.Li([html.B('Bottom Panel: '), 'Simulation controls and timeline slider'])
                ])
            ])
        ], style={'padding': '20px', 'maxWidth': '800px', 'margin': '0 auto'})
    ])

# Navigation callback
@callback(
    [Output('main-content', 'children'),
     Output('nav-home', 'className'),
     Output('nav-userguide', 'className')],
    [Input('nav-home', 'n_clicks'),
     Input('nav-userguide', 'n_clicks')],
    prevent_initial_call=True
)
def navigate_pages(home_clicks, userguide_clicks):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'nav-home'
    
    if triggered_id == 'nav-userguide':
        return create_userguide_layout(), 'tab-button', 'tab-button active'
    else:
        return create_home_layout(), 'tab-button active', 'tab-button'

# Initialize with home page
@callback(
    Output('main-content', 'children', allow_duplicate=True),
    Input('main-content', 'id'),
    prevent_initial_call='initial_duplicate'
)
def init_main_content(_):
    return create_home_layout()

# Dropdown toggle callback
@callback(
    Output('scenario-dropdown', 'style'),
    Input('set-scenario-btn', 'n_clicks'),
    State('scenario-dropdown', 'style'),
    prevent_initial_call=True
)
def toggle_scenario_dropdown(n_clicks, current_style):
    if n_clicks:
        if current_style.get('display') == 'none':
            current_style['display'] = 'block'
        else:
            current_style['display'] = 'none'
    return current_style

# Modal for Disease Parameters
@callback(
    Output('disease-params-modal', 'is_open'),
    [Input('disease-params-btn', 'n_clicks'),
     Input('disease-params-close', 'n_clicks'),
     Input('disease-params-save', 'n_clicks')],
    [State('disease-params-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_disease_params_modal(open_click, close_click, save_click, is_open):
    return not is_open

# Disease Parameters Modal Component
disease_params_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Disease Parameters")),
    dbc.ModalBody([
        html.Div([
            html.Label('Disease Name'),
            dcc.Input(id='disease-name', type='text', value='COVID-19', style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Reproduction Number (R₀)'),
            dcc.Input(id='reproduction-number', type='number', value=2.5, step=0.1, style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Beta Scale'),
            dcc.Input(id='beta-scale', type='number', value=1.0, step=0.1, style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Tau'),
            dcc.Input(id='tau', type='number', value=5.1, step=0.1, style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Kappa'),
            dcc.Input(id='kappa', type='number', value=1.0, step=0.1, style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Gamma'),
            dcc.Input(id='gamma', type='number', value=0.1, step=0.01, style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Chi'),
            dcc.Input(id='chi', type='number', value=0.5, step=0.1, style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Rho'),
            dcc.Input(id='rho', type='number', value=0.8, step=0.1, style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Nu'),
            dcc.Input(id='nu', type='number', value=0.01, step=0.001, style={'width': '100%'})
        ])
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="disease-params-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="disease-params-close", className="ms-auto", n_clicks=0)
    ])
], id="disease-params-modal", is_open=False)

# Initial Cases Modal Component  
initial_cases_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Initial Cases")),
    dbc.ModalBody([
        html.Div([
            html.Label('Select Counties'),
            dcc.Dropdown(
                id='initial-counties',
                options=[{'label': county, 'value': county} for county in texas_counties],
                multi=True,
                placeholder='Select counties for initial cases',
                style={'marginBottom': '10px'}
            )
        ]),
        html.Div([
            html.Label('Cases per County'),
            dcc.Input(id='initial-cases-count', type='number', value=100, min=1, style={'width': '100%'})
        ])
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="initial-cases-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="initial-cases-close", className="ms-auto", n_clicks=0)
    ])
], id="initial-cases-modal", is_open=False)

# Add modals to layout
app.layout.children.extend([disease_params_modal, initial_cases_modal])

# Initial Cases Modal toggle
@callback(
    Output('initial-cases-modal', 'is_open'),
    [Input('initial-cases-btn', 'n_clicks'),
     Input('initial-cases-close', 'n_clicks'),
     Input('initial-cases-save', 'n_clicks')],
    [State('initial-cases-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_initial_cases_modal(open_click, close_click, save_click, is_open):
    return not is_open

# Save parameters callback
@callback(
    [Output('displayed-parameters', 'children'),
     Output('play-pause-btn', 'disabled'),
     Output('has-set-scenario', 'data')],
    [Input('disease-params-save', 'n_clicks'),
     Input('initial-cases-save', 'n_clicks')],
    [State('disease-name', 'value'),
     State('reproduction-number', 'value'),
     State('initial-counties', 'value'),
     State('initial-cases-count', 'value')],
    prevent_initial_call=True
)
def save_parameters(disease_save, cases_save, disease_name, r0, counties, cases_count):
    if disease_save or cases_save:
        params_display = [
            html.H6('Disease Parameters'),
            html.P(f'Disease: {disease_name or "COVID-19"}'),
            html.P(f'R₀: {r0 or 2.5}'),
            html.Hr(),
            html.H6('Initial Cases'),
            html.P(f'Counties: {len(counties) if counties else 0} selected'),
            html.P(f'Cases per County: {cases_count or 100}')
        ]
        return params_display, False, True
    return dash.no_update, True, False

# Play/Pause simulation callback
@callback(
    [Output('simulation-state', 'data'),
     Output('play-pause-btn', 'children'),
     Output('play-pause-btn', 'style'),
     Output('simulation-interval', 'disabled'),
     Output('timeline-slider', 'disabled', allow_duplicate=True)],
    Input('play-pause-btn', 'n_clicks'),
    [State('simulation-state', 'data'),
     State('has-set-scenario', 'data'),
     State('disease-name', 'value'),
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
     State('antiviral-effectiveness', 'value'),
     State('antiviral-stockpile', 'value')],
    prevent_initial_call=True
)
def toggle_simulation(n_clicks, sim_state, has_scenario, disease_name, r0, beta_scale, tau, kappa, gamma, chi, rho, nu, 
                     counties, cases_count, npis, vaccine_eff, vaccine_adh, vaccine_stock, antiviral_eff, antiviral_stock):
    if n_clicks and has_scenario:
        is_running = sim_state.get('isRunning', False)
        
        if not is_running:
            # Start simulation - call backend API
            try:
                # Format initial infected data
                initial_infected = []
                if counties and cases_count:
                    for county in counties:
                        # Convert county name to FIPS if needed
                        county_fips = county if county.isdigit() else f"48{hash(county) % 1000:03d}"  # Mock FIPS conversion
                        initial_infected.append({
                            'fips_id': county_fips,
                            'cases': cases_count
                        })
                
                # Format NPIs
                npi_data = []
                if npis:
                    for npi in npis:
                        npi_data.append({
                            'type': npi,
                            'effectiveness': 0.5,
                            'start_day': 5,
                            'duration': 30
                        })
                
                # Prepare API payload
                payload = {
                    'disease_name': disease_name or 'COVID-19',
                    'R0': r0 or 2.5,
                    'beta_scale': beta_scale or 1.0,
                    'tau': tau or 5.1,
                    'kappa': kappa or 1.0,
                    'gamma': gamma or 0.1,
                    'chi': chi or 0.5,
                    'rho': rho or 0.8,
                    'nu': nu or 0.01,
                    'initial_infected': json.dumps(initial_infected),
                    'npis': json.dumps(npi_data),
                    'antiviral_effectiveness': (antiviral_eff or 75) / 100,
                    'antiviral_stockpile': antiviral_stock or 500000,
                    'antiviral_wastage_factor': 0.05,
                    'vaccine_effectiveness': (vaccine_eff or 85) / 100,
                    'vaccine_adherence': (vaccine_adh or 70) / 100,
                    'vaccine_stockpile': vaccine_stock or 1000000,
                    'vaccine_wastage_factor': 0.1,
                    'vaccine_pro_rata': 'proportional'
                }
                
                # Call backend API
                response = requests.post(f'{API_BASE_URL}/api/pet/', json=payload)
                if response.status_code == 201:
                    sim_id = response.json().get('id')
                    
                    # Start simulation
                    run_response = requests.get(f'{API_BASE_URL}/api/pet/{sim_id}/run')
                    if run_response.status_code == 202:
                        task_id = run_response.json().get('task_id')
                        
                        # Success - start simulation
                        new_state = {**sim_state, 'isRunning': True, 'currentIndex': 0, 'id': sim_id, 'taskId': task_id}
                        button_style = {
                            'padding': '10px 30px',
                            'fontSize': '16px',
                            'backgroundColor': '#ffc107',
                            'color': 'black',
                            'border': 'none',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'marginRight': '20px'
                        }
                        return new_state, 'Pause', button_style, False, False, False
                
            except Exception as e:
                logger.error(f"Error starting simulation: {e}")
                # Fall back to mock simulation
                pass
            
            # Fallback to mock simulation
            new_state = {**sim_state, 'isRunning': True, 'currentIndex': 0}
            button_style = {
                'padding': '10px 30px',
                'fontSize': '16px',
                'backgroundColor': '#ffc107',
                'color': 'black',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'marginRight': '20px'
            }
            return new_state, 'Pause', button_style, False, False
        else:
            # Pause simulation
            task_id = sim_state.get('taskId')
            if task_id:
                try:
                    requests.get(f'{API_BASE_URL}/api/delete/{task_id}')
                except:
                    pass
            
            new_state = {**sim_state, 'isRunning': False}
            button_style = {
                'padding': '10px 30px',
                'fontSize': '16px',
                'backgroundColor': '#28a745',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'marginRight': '20px'
            }
            return new_state, 'Play', button_style, True, True
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Simulation data fetching callback
@callback(
    [Output('event-data', 'data'),
     Output('timeline-slider', 'max'),
     Output('timeline-slider', 'disabled')],
    Input('simulation-interval', 'n_intervals'),
    [State('simulation-state', 'data'),
     State('event-data', 'data')],
    prevent_initial_call=True
)
def fetch_simulation_data(n_intervals, sim_state, event_data):
    if sim_state.get('isRunning', False):
        current_day = len(event_data)
        
        # Try to fetch real data from API
        try:
            response = requests.get(f'{API_BASE_URL}/api/output/{current_day}')
            if response.status_code == 200:
                api_data = response.json()
                
                # Process API response
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
                return updated_event_data, len(updated_event_data), False
                
        except Exception as e:
            logger.debug(f"API fetch failed, using mock data: {e}")
            
        # Fallback to mock data generation
        if current_day < 30:  # Generate mock data for 30 days
            day_data = {
                'day': current_day,
                'counties': [
                    {
                        'fips': '48201',  # Harris County
                        'infected': current_day * 10 + 50,
                        'deceased': current_day * 2,
                        'infectedPercent': min((current_day * 0.1 + 0.5), 5.0),
                        'deceasedPercent': min((current_day * 0.02), 1.0)
                    },
                    {
                        'fips': '48113',  # Dallas County
                        'infected': current_day * 8 + 30,
                        'deceased': current_day * 1,
                        'infectedPercent': min((current_day * 0.08 + 0.3), 4.0),
                        'deceasedPercent': min((current_day * 0.01), 0.8)
                    }
                ],
                'totalSusceptible': 29000000 - (current_day * 50),
                'totalExposed': current_day * 20,
                'totalAsymptomaticCount': current_day * 15,
                'totalTreatableCount': current_day * 10,
                'totalInfectedCount': current_day * 18 + 80,
                'totalRecoveredCount': max(0, (current_day - 5) * 15),
                'totalDeceased': current_day * 3
            }
            
            updated_event_data = event_data + [day_data]
            return updated_event_data, len(updated_event_data), False
    
    return event_data, max(30, len(event_data)), len(event_data) == 0

# Create visualizations
def create_empty_map():
    fig = go.Figure()
    fig.update_layout(
        title="Texas Counties - No Data Available",
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
        ),
        height=400
    )
    return fig

def create_empty_chart():
    fig = go.Figure()
    fig.update_layout(
        title="Epidemic Curve - No Data Available",
        xaxis_title="Day",
        yaxis_title="Count",
        height=300
    )
    return fig

# Map callback
@callback(
    Output('spread-map', 'figure'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value')]
)
def update_map(event_data, timeline_value, view_type):
    if not event_data or timeline_value is None or timeline_value >= len(event_data):
        return create_empty_map()
    
    current_data = event_data[timeline_value]
    counties_data = current_data.get('counties', [])
    
    if not counties_data:
        return create_empty_map()
    
    # Create Texas choropleth map
    fig = go.Figure()
    
    # Add Texas state shape
    fig.add_trace(go.Choropleth(
        locations=['TX'],
        z=[current_data.get('totalInfectedCount', 0)],
        locationmode='USA-states',
        colorscale='Reds',
        text=[f"Texas - Day {current_data.get('day', 0)}"],
        hovertemplate='<b>%{text}</b><br>Total Infected: %{z}<extra></extra>',
        showscale=True,
        colorbar=dict(title=f"Infected ({'%' if view_type == 'percent' else 'Count'})")
    ))
    
    fig.update_layout(
        title=f"Day {current_data.get('day', 0)} - Texas Disease Spread ({'Percentage' if view_type == 'percent' else 'Count'} View)",
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
        ),
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

# Chart callback
@callback(
    Output('line-chart', 'figure'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value')]
)
def update_chart(event_data, timeline_value):
    if not event_data:
        return create_empty_chart()
    
    days = [d['day'] for d in event_data]
    susceptible = [d.get('totalSusceptible', 0) for d in event_data]
    exposed = [d.get('totalExposed', 0) for d in event_data]
    asymptomatic = [d.get('totalAsymptomaticCount', 0) for d in event_data]
    treatable = [d.get('totalTreatableCount', 0) for d in event_data]
    infected = [d.get('totalInfectedCount', 0) for d in event_data]
    recovered = [d.get('totalRecoveredCount', 0) for d in event_data]
    deceased = [d.get('totalDeceased', 0) for d in event_data]
    
    fig = go.Figure()
    
    # Add traces for SEATIRD compartments
    fig.add_trace(go.Scatter(x=days, y=susceptible, name='Susceptible', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=days, y=exposed, name='Exposed', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=days, y=asymptomatic, name='Asymptomatic', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=days, y=treatable, name='Treatable', line=dict(color='purple')))
    fig.add_trace(go.Scatter(x=days, y=infected, name='Infected', line=dict(color='red', width=3)))
    fig.add_trace(go.Scatter(x=days, y=recovered, name='Recovered', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=days, y=deceased, name='Deceased', line=dict(color='black')))
    
    # Add vertical line for current day
    if timeline_value is not None and timeline_value < len(days):
        fig.add_vline(x=timeline_value, line_dash="dash", line_color="gray", annotation_text=f"Day {timeline_value}")
    
    fig.update_layout(
        title="Epidemic Curve - SEATIRD Model",
        xaxis_title="Day",
        yaxis_title="Population Count",
        height=300,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='x unified'
    )
    
    return fig

# Table callback
@callback(
    Output('spread-table', 'children'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value')]
)
def update_table(event_data, timeline_value, view_type):
    if not event_data or timeline_value is None or timeline_value >= len(event_data):
        return html.P('No data available', style={'color': '#6c757d', 'fontStyle': 'italic'})
    
    current_data = event_data[timeline_value]
    counties_data = current_data.get('counties', [])
    
    if not counties_data:
        return html.P('No county data available', style={'color': '#6c757d', 'fontStyle': 'italic'})
    
    # Create table data
    table_data = []
    for county in counties_data:
        fips = county.get('fips', 'Unknown')
        county_name = f"County {fips[-3:]}" if fips else "Unknown"
        
        if view_type == 'percent':
            infected_val = f"{county.get('infectedPercent', 0):.1f}%"
            deceased_val = f"{county.get('deceasedPercent', 0):.1f}%"
        else:
            infected_val = f"{county.get('infected', 0):,}"
            deceased_val = f"{county.get('deceased', 0):,}"
        
        table_data.append([county_name, infected_val, deceased_val])
    
    # Create table
    table = html.Table([
        html.Thead([
            html.Tr([
                html.Th('County', style={'padding': '8px', 'textAlign': 'left'}),
                html.Th('Infected', style={'padding': '8px', 'textAlign': 'left'}),
                html.Th('Deceased', style={'padding': '8px', 'textAlign': 'left'})
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(row[0], style={'padding': '8px'}),
                html.Td(row[1], style={'padding': '8px'}),
                html.Td(row[2], style={'padding': '8px'})
            ]) for row in table_data
        ])
    ], style={'width': '100%', 'borderCollapse': 'collapse'})
    
    return table

# Timeline slider update callback
@callback(
    Output('timeline-slider', 'value'),
    Input('simulation-state', 'data'),
    State('event-data', 'data'),
    prevent_initial_call=True
)
def update_timeline_position(sim_state, event_data):
    if sim_state.get('isRunning', False) and event_data:
        return len(event_data) - 1
    return dash.no_update


# Expose server for deployment
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)