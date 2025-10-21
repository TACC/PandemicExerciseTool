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

# Load Texas counties and mapping
def load_texas_data():
    """Load Texas counties and county-to-FIPS mapping"""
    try:
        # Load county names
        with open('../frontend/src/data/texasCounties.js', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        counties = []
        for line in lines:
            line = line.strip()
            if line.startswith("'") and (line.endswith("',") or line.endswith("'")):
                county = line[1:-2] if line.endswith("',") else line[1:-1]
                counties.append(county)
        
        # Load county mapping
        with open('../frontend/src/data/texasMapping.json', 'r') as f:
            county_mapping = json.load(f)
        
        return counties, county_mapping
    except Exception as e:
        logger.warning(f"Could not load Texas data: {e}")
        return ['Harris', 'Dallas', 'Tarrant', 'Bexar'], {'Harris': '201', 'Dallas': '113'}

texas_counties, texas_mapping = load_texas_data()

# Age group constants (matching React exactly)
AGE_GROUPS = [
    {'value': '0-4 years', 'label': '0-4 years'},
    {'value': '5-24 years', 'label': '5-24 years'},
    {'value': '25-49 years', 'label': '25-49 years'},
    {'value': '50-64 years', 'label': '50-64 years'},
    {'value': '65+ years', 'label': '65+ years'}
]

AGE_GROUP_MAPPING = {
    '0-4 years': '0',
    '5-24 years': '1', 
    '25-49 years': '2',
    '50-64 years': '3',
    '65+ years': '4'
}

# Preset scenarios (matching React exactly)
PRESET_SCENARIOS = {
    'slow_mild_2009': {
        'name': 'Slow Transmission, Mild Severity (2009 H1N1)',
        'disease_name': '2009 H1N1',
        'R0': 1.2,
        'beta_scale': 10.0,
        'tau': 1.2,
        'kappa': 1.9,
        'gamma': 4.1,
        'chi': 1.0,
        'rho': 0.39,
        'nu': [0.000022319, 0.000040975, 0.000083729, 0.000061809, 0.000008978]
    },
    'slow_high_1918': {
        'name': 'Slow Transmission, High Severity (1918 Influenza)',
        'disease_name': '1918 Influenza',
        'R0': 1.2,
        'beta_scale': 10.0,
        'tau': 1.2,
        'kappa': 1.9,
        'gamma': 4.1,
        'chi': 1.0,
        'rho': 0.39,
        'nu': [0.05, 0.002, 0.01, 0.05, 0.15]
    },
    'fast_mild_2009': {
        'name': 'Fast Transmission, Mild Severity (2009 H1N1)',
        'disease_name': '2009 H1N1',
        'R0': 2.5,
        'beta_scale': 10.0,
        'tau': 1.2,
        'kappa': 1.9,
        'gamma': 4.1,
        'chi': 1.0,
        'rho': 0.39,
        'nu': [0.000022319, 0.000040975, 0.000083729, 0.000061809, 0.000008978]
    },
    'fast_high_1918': {
        'name': 'Fast Transmission, High Severity (1918 Influenza)',
        'disease_name': '1918 Influenza',
        'R0': 2.5,
        'beta_scale': 10.0,
        'tau': 1.2,
        'kappa': 1.9,
        'gamma': 4.1,
        'chi': 1.0,
        'rho': 0.39,
        'nu': [0.05, 0.002, 0.01, 0.05, 0.15]
    }
}

# App Layout - Exact match to React structure
app.layout = html.Div([
    # Stores for state management (like React useState)
    dcc.Store(id='simulation-state', data={'isRunning': False, 'currentIndex': 0, 'taskId': None, 'id': None}),
    dcc.Store(id='event-data', data=[]),
    dcc.Store(id='view-type', data='percent'),
    dcc.Store(id='disease-parameters', data={}),
    dcc.Store(id='initial-cases-data', data=[]),
    dcc.Store(id='npi-data', data=[]),
    dcc.Store(id='antiviral-data', data={}),
    dcc.Store(id='vaccine-data', data={}),
    dcc.Store(id='displayed-tab', data='scenario'),
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
                        className='parameters-button'),
                        
                        # Dropdown menu
                        html.Div([
                            html.Button('Disease Parameters', 
                                id='disease-params-btn',
                                className='dropdown-items'),
                            html.Button('Initial Cases',
                                id='initial-cases-btn', 
                                className='dropdown-items')
                        ],
                        id='scenario-dropdown',
                        style={'display': 'none'})
                    ], style={'position': 'relative', 'marginBottom': '10px'}),
                    
                    # Interventions dropdown (like React Interventions component)
                    html.Div([
                        html.Button([
                            html.Span('Interventions', className='dropdown-text'),
                            html.Span('▾', className='dropdown-arrow')
                        ], 
                        id='interventions-btn',
                        className='parameters-button'),
                        
                        # Dropdown menu
                        html.Div([
                            html.Button('Non-Pharmaceutical', 
                                id='npi-btn',
                                className='dropdown-items'),
                            html.Button('Antivirals',
                                id='antivirals-btn', 
                                className='dropdown-items'),
                            html.Button('Vaccines',
                                id='vaccines-btn', 
                                className='dropdown-items')
                        ],
                        id='interventions-dropdown',
                        style={'display': 'none'})
                    ], style={'position': 'relative', 'marginBottom': '10px'}),
                    
                    # DisplayedParameters section (like React DisplayedParameters component)
                    html.Div([
                        # Tab buttons
                        html.Div([
                            html.Button('Scenario', 
                                id='scenario-tab-btn',
                                className='tab-btn active-tab',
                                style={'marginRight': '5px'}),
                            html.Button('Interventions', 
                                id='interventions-tab-btn',
                                className='tab-btn')
                        ], style={'marginBottom': '10px'}),
                        
                        # Tab content
                        html.Div(id='displayed-parameters-content', children=[
                            html.P('No scenario set yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})
                        ])
                    ], className='displayed-parameters-panel')
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
                        className='play-pause-button'
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
                ], className='footer-controls')
            ], style={'marginTop': '20px'})
        ], className='row')
    ])

# User Guide layout
def create_userguide_layout():
    return html.Div([
        html.Div([
            html.H2('User Guide', style={'marginBottom': '20px', 'color': '#102c41'}),
            html.Div([
                html.H4('How to Use the Pandemic Simulator'),
                html.Ol([
                    html.Li([html.B('Set Disease Parameters: '), 'Configure the disease characteristics including reproduction number, incubation period, and other epidemiological parameters.']),
                    html.Li([html.B('Select Initial Cases: '), 'Choose which Texas counties will have initial cases and specify the number of cases per county and age group.']),
                    html.Li([html.B('Configure Interventions: '), 'Set up non-pharmaceutical interventions, antivirals, and vaccines.']),
                    html.Li([html.B('Run Simulation: '), 'Click the "Play" button to start the simulation. You can pause it at any time.']),
                    html.Li([html.B('View Results: '), 'Monitor the outbreak progression through the map, epidemic curve, and county data table.'])
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
                ])
            ])
        ], style={'padding': '20px', 'maxWidth': '800px', 'margin': '0 auto'})
    ])

# Disease Parameters Modal Component
disease_params_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Disease Parameters")),
    dbc.ModalBody([
        # Preset scenarios dropdown
        html.Div([
            html.Label('Load from Catalog', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                id='preset-scenario-dropdown',
                options=[
                    {'label': scenario['name'], 'value': key} 
                    for key, scenario in PRESET_SCENARIOS.items()
                ],
                placeholder='Select a preset scenario...',
                style={'marginBottom': '15px'}
            )
        ]),
        
        html.Hr(),
        
        # Disease parameters form
        html.Div([
            html.Label('Scenario Name'),
            dcc.Input(id='scenario-name', type='text', value='', 
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Reproduction Number (R₀)'),
            html.Small(' - Average number of secondary infections in a susceptible population', 
                style={'color': '#6c757d'}),
            dcc.Input(id='reproduction-number', type='number', value=1.2, step=0.1, min=0,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Latency period (days)'),
            html.Small(' - Average number of days spent asymptomatic immediately after infection',
                style={'color': '#6c757d'}),
            dcc.Input(id='latency-period', type='number', value=1.2, step=0.1, min=0,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Asymptomatic period (days)'),
            html.Small(' - Average number of days spent infectious, but not yet symptomatic',
                style={'color': '#6c757d'}),
            dcc.Input(id='asymptomatic-period', type='number', value=1.9, step=0.1, min=0,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Symptomatic period (days)'),
            html.Small(' - Average number of days spent symptomatic and infectious',
                style={'color': '#6c757d'}),
            dcc.Input(id='symptomatic-period', type='number', value=4.1, step=0.1, min=0,
                style={'width': '100%', 'marginBottom': '15px'})
        ]),
        
        # Age-specific CFR section
        html.Div([
            html.Label('Infection fatality rate (proportion)', style={'fontWeight': 'bold'}),
            html.Small(' - Proportion of infections that lead to death', 
                style={'color': '#6c757d', 'display': 'block', 'marginBottom': '10px'}),
            
            # CFR inputs for each age group
            html.Div([
                html.Label('0-4 years', style={'fontSize': '14px'}),
                dcc.Input(id='cfr-0-4', type='number', value=0.000022319, 
                    step=0.000000001, min=0, max=100,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('5-24 years', style={'fontSize': '14px'}),
                dcc.Input(id='cfr-5-24', type='number', value=0.000040975,
                    step=0.000000001, min=0, max=100,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('25-49 years', style={'fontSize': '14px'}),
                dcc.Input(id='cfr-25-49', type='number', value=0.000083729,
                    step=0.000000001, min=0, max=100,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('50-64 years', style={'fontSize': '14px'}),
                dcc.Input(id='cfr-50-64', type='number', value=0.000061809,
                    step=0.000000001, min=0, max=100,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('65+ years', style={'fontSize': '14px'}),
                dcc.Input(id='cfr-65-plus', type='number', value=0.000008978,
                    step=0.000000001, min=0, max=100,
                    style={'width': '100%'})
            ])
        ])
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="disease-params-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="disease-params-close", className="ms-auto", n_clicks=0)
    ])
], id="disease-params-modal", is_open=False, size="lg")

# Initial Cases Modal Component  
initial_cases_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Initial Cases")),
    dbc.ModalBody([
        html.Div([
            html.Label('Location'),
            dcc.Dropdown(
                id='initial-location',
                options=[{'label': county, 'value': county} for county in texas_counties],
                placeholder='Search for a county...',
                style={'marginBottom': '10px'}
            )
        ]),
        html.Div([
            html.Label('Number of Cases'),
            dcc.Input(id='initial-cases-count', type='number', value=100, min=1, 
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Age Group'),
            dcc.Dropdown(
                id='initial-age-group',
                options=AGE_GROUPS,
                value='0-4 years',
                style={'marginBottom': '15px'}
            )
        ]),
        
        html.Button('Add Initial Case', id='add-initial-case-btn', 
            className='btn btn-secondary', style={'marginBottom': '15px'}),
        
        # Table showing added initial cases
        html.Div(id='initial-cases-table')
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="initial-cases-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="initial-cases-close", className="ms-auto", n_clicks=0)
    ])
], id="initial-cases-modal", is_open=False, size="lg")

# Add modals to layout
app.layout.children.extend([disease_params_modal, initial_cases_modal])

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

# Dropdown toggle callbacks
@callback(
    Output('scenario-dropdown', 'style'),
    Input('set-scenario-btn', 'n_clicks'),
    State('scenario-dropdown', 'style'),
    prevent_initial_call=True
)
def toggle_scenario_dropdown(n_clicks, current_style):
    if n_clicks:
        display = 'none' if current_style.get('display') == 'block' else 'block'
        return {**current_style, 'display': display}
    return current_style

@callback(
    Output('interventions-dropdown', 'style'),
    Input('interventions-btn', 'n_clicks'),
    State('interventions-dropdown', 'style'),
    prevent_initial_call=True
)
def toggle_interventions_dropdown(n_clicks, current_style):
    if n_clicks:
        display = 'none' if current_style.get('display') == 'block' else 'block'
        return {**current_style, 'display': display}
    return current_style

# Modal toggle callbacks
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

# Preset scenario loading callback
@callback(
    [Output('scenario-name', 'value'),
     Output('reproduction-number', 'value'),
     Output('latency-period', 'value'),
     Output('asymptomatic-period', 'value'),
     Output('symptomatic-period', 'value'),
     Output('cfr-0-4', 'value'),
     Output('cfr-5-24', 'value'),
     Output('cfr-25-49', 'value'),
     Output('cfr-50-64', 'value'),
     Output('cfr-65-plus', 'value')],
    Input('preset-scenario-dropdown', 'value'),
    prevent_initial_call=True
)
def load_preset_scenario(preset_key):
    if preset_key and preset_key in PRESET_SCENARIOS:
        scenario = PRESET_SCENARIOS[preset_key]
        return (
            scenario['disease_name'],
            scenario['R0'],
            scenario['tau'],
            scenario['kappa'],
            scenario['gamma'],
            scenario['nu'][0],
            scenario['nu'][1],
            scenario['nu'][2],
            scenario['nu'][3],
            scenario['nu'][4]
        )
    return [dash.no_update] * 10

# Initial cases management callbacks
@callback(
    [Output('initial-cases-data', 'data'),
     Output('initial-cases-table', 'children')],
    [Input('add-initial-case-btn', 'n_clicks'),
     Input({'type': 'remove-case-btn', 'index': ALL}, 'n_clicks')],
    [State('initial-location', 'value'),
     State('initial-cases-count', 'value'),
     State('initial-age-group', 'value'),
     State('initial-cases-data', 'data')],
    prevent_initial_call=True
)
def manage_initial_cases(add_clicks, remove_clicks, location, cases_count, age_group, current_data):
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None
    
    if 'add-initial-case-btn' in triggered_id and location and cases_count:
        # Add new case
        fips_id = texas_mapping.get(location, '0')
        age_group_id = AGE_GROUP_MAPPING.get(age_group, '0')
        
        new_case = {
            'id': len(current_data),
            'location': location,
            'fips_id': fips_id,
            'cases': cases_count,
            'age_group': age_group,
            'age_group_id': age_group_id
        }
        current_data.append(new_case)
    
    elif 'remove-case-btn' in triggered_id:
        # Remove case by index
        import re
        match = re.search(r'"index":(\d+)', triggered_id)
        if match:
            remove_index = int(match.group(1))
            current_data = [case for case in current_data if case['id'] != remove_index]
    
    # Create table
    if current_data:
        table_rows = []
        for case in current_data:
            table_rows.append(
                html.Tr([
                    html.Td(case['location']),
                    html.Td(f"{case['cases']} aged {case['age_group']}"),
                    html.Td(
                        html.Button('Remove', 
                            id={'type': 'remove-case-btn', 'index': case['id']},
                            className='btn btn-sm btn-danger')
                    )
                ])
            )
        
        table = html.Table([
            html.Thead([
                html.Tr([
                    html.Th('Location'),
                    html.Th('Cases'),
                    html.Th('Action')
                ])
            ]),
            html.Tbody(table_rows)
        ], className='table table-striped')
    else:
        table = html.P('No initial cases added yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})
    
    return current_data, table

# Disease parameters save callback
@callback(
    [Output('disease-parameters', 'data'),
     Output('displayed-parameters-content', 'children', allow_duplicate=True),
     Output('play-pause-btn', 'disabled', allow_duplicate=True)],
    Input('disease-params-save', 'n_clicks'),
    [State('scenario-name', 'value'),
     State('reproduction-number', 'value'),
     State('latency-period', 'value'),
     State('asymptomatic-period', 'value'),
     State('symptomatic-period', 'value'),
     State('cfr-0-4', 'value'),
     State('cfr-5-24', 'value'),
     State('cfr-25-49', 'value'),
     State('cfr-50-64', 'value'),
     State('cfr-65-plus', 'value'),
     State('initial-cases-data', 'data'),
     State('displayed-tab', 'data')],
    prevent_initial_call=True
)
def save_disease_parameters(n_clicks, scenario_name, r0, tau, kappa, gamma, 
                          cfr_0_4, cfr_5_24, cfr_25_49, cfr_50_64, cfr_65_plus,
                          initial_cases, displayed_tab):
    if n_clicks:
        # Save disease parameters
        disease_params = {
            'scenario_name': scenario_name or 'Custom Scenario',
            'R0': r0 or 1.2,
            'tau': tau or 1.2,
            'kappa': kappa or 1.9,
            'gamma': gamma or 4.1,
            'chi': 1.0,  # Default therapeutic window
            'rho': 0.39,  # Default treatment seeking rate
            'nu': [cfr_0_4 or 0, cfr_5_24 or 0, cfr_25_49 or 0, cfr_50_64 or 0, cfr_65_plus or 0]
        }
        
        # Update displayed parameters
        if displayed_tab == 'scenario':
            content = create_scenario_display(disease_params, initial_cases)
        else:
            content = html.P('No interventions set yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})
        
        # Enable play button if we have both parameters and initial cases
        play_disabled = not (disease_params and initial_cases)
        
        return disease_params, content, play_disabled
    
    return dash.no_update, dash.no_update, dash.no_update

# Tab switching callback
@callback(
    [Output('displayed-parameters-content', 'children', allow_duplicate=True),
     Output('scenario-tab-btn', 'className'),
     Output('interventions-tab-btn', 'className'),
     Output('displayed-tab', 'data')],
    [Input('scenario-tab-btn', 'n_clicks'),
     Input('interventions-tab-btn', 'n_clicks')],
    [State('disease-parameters', 'data'),
     State('initial-cases-data', 'data'),
     State('npi-data', 'data'),
     State('antiviral-data', 'data'),
     State('vaccine-data', 'data')],
    prevent_initial_call=True
)
def switch_displayed_tab(scenario_clicks, interventions_clicks, disease_params, initial_cases, 
                        npi_data, antiviral_data, vaccine_data):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'scenario-tab-btn'
    
    if triggered_id == 'interventions-tab-btn':
        content = create_interventions_display(npi_data, antiviral_data, vaccine_data)
        return content, 'tab-btn', 'tab-btn active-tab', 'interventions'
    else:
        content = create_scenario_display(disease_params, initial_cases)
        return content, 'tab-btn active-tab', 'tab-btn', 'scenario'

def create_scenario_display(disease_params, initial_cases):
    """Create scenario tab display content"""
    if not disease_params and not initial_cases:
        return html.P('No scenario set yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})
    
    content = []
    
    # Disease parameters section
    if disease_params:
        content.extend([
            html.H6('Disease Parameters', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.P(f"Scenario: {disease_params.get('scenario_name', 'Custom')}"),
            html.P(f"Reproduction Number: {disease_params.get('R0', 0)}"),
            html.P(f"Latency Period: {disease_params.get('tau', 0)} days"),
            html.P(f"Asymptomatic Period: {disease_params.get('kappa', 0)} days"),
            html.P(f"Symptomatic Period: {disease_params.get('gamma', 0)} days"),
            html.P('Case Fatality Rate:'),
            html.Ul([
                html.Li(f"0-4: {disease_params.get('nu', [0,0,0,0,0])[0]:.9f}"),
                html.Li(f"5-24: {disease_params.get('nu', [0,0,0,0,0])[1]:.9f}"),
                html.Li(f"25-49: {disease_params.get('nu', [0,0,0,0,0])[2]:.9f}"),
                html.Li(f"50-64: {disease_params.get('nu', [0,0,0,0,0])[3]:.9f}"),
                html.Li(f"65+: {disease_params.get('nu', [0,0,0,0,0])[4]:.9f}")
            ], style={'marginLeft': '20px', 'marginBottom': '15px'})
        ])
    
    # Initial cases section
    if initial_cases:
        content.extend([
            html.H6('Initial Cases', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.Ul([
                html.Li(f"{case['cases']} aged {case['age_group']} in {case['location']}")
                for case in initial_cases
            ], style={'marginLeft': '20px'})
        ])
    
    if not content:
        return html.P('No scenario set yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})
    
    return html.Div(content)

def create_interventions_display(npi_data, antiviral_data, vaccine_data):
    """Create interventions tab display content"""
    return html.P('No interventions set yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})

# Placeholder callbacks for remaining functionality
@callback(
    Output('spread-map', 'figure'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value')]
)
def update_map(event_data, timeline_value, view_type):
    fig = go.Figure()
    fig.update_layout(
        title="Texas Counties - Interactive Pandemic Simulation",
        geo=dict(scope='usa', projection=go.layout.geo.Projection(type='albers usa')),
        height=400
    )
    return fig

@callback(
    Output('line-chart', 'figure'),
    Input('event-data', 'data')
)
def update_chart(event_data):
    fig = go.Figure()
    fig.update_layout(
        title="Epidemic Curve - SEATIRD Model",
        xaxis_title="Day",
        yaxis_title="Population Count",
        height=300
    )
    return fig

@callback(
    Output('spread-table', 'children'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value')]
)
def update_table(event_data, timeline_value, view_type):
    return html.P('No data available', style={'color': '#6c757d', 'fontStyle': 'italic'})

# Expose server for deployment
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8051)