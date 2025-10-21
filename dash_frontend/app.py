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
API_BASE_URL = os.getenv('API_BASE_URL', 'http://django-backend-dash:8000')

# Load Texas counties and mapping
def load_texas_data():
    """Load Texas counties and county-to-FIPS mapping"""
    try:
        # Load county names
        with open('texasCounties.js', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        counties = []
        for line in lines:
            line = line.strip()
            if line.startswith("'") and (line.endswith("',") or line.endswith("'")):
                county = line[1:-2] if line.endswith("',") else line[1:-1]
                counties.append(county)
        
        # Load county mapping
        with open('texasMapping.json', 'r') as f:
            county_mapping = json.load(f)
        
        return counties, county_mapping
    except Exception as e:
        logger.warning(f"Could not load Texas data: {e}")
        return ['Harris', 'Dallas', 'Tarrant', 'Bexar'], {'Harris': '201', 'Dallas': '113'}

def load_texas_geojson():
    """Load Texas counties GeoJSON data"""
    try:
        with open('texasOutline.json', 'r') as f:
            texas_geojson = json.load(f)
        return texas_geojson
    except Exception as e:
        logger.warning(f"Could not load Texas GeoJSON: {e}")
        return None

texas_counties, texas_mapping = load_texas_data()
texas_geojson = load_texas_geojson()

def get_county_color(infected_value, view_type='count'):
    """Get color for county based on infection data"""
    if view_type == 'percent':
        # Color scale for percentage values
        if infected_value > 40:
            return '#800026'
        elif infected_value > 30:
            return '#BD0026'
        elif infected_value > 20:
            return '#E31A1C'
        elif infected_value > 10:
            return '#FC4E2A'
        elif infected_value > 5:
            return '#FD8D3C'
        elif infected_value > 2.5:
            return '#FEB24C'
        elif infected_value > 1:
            return '#FED976'
        else:
            return '#FFEDA0'
    else:
        # Color scale for count values (matching React version)
        if infected_value > 5000:
            return '#800026'
        elif infected_value > 2000:
            return '#BD0026'
        elif infected_value > 1000:
            return '#E31A1C'
        elif infected_value > 500:
            return '#FC4E2A'
        elif infected_value > 200:
            return '#FD8D3C'
        elif infected_value > 100:
            return '#FEB24C'
        elif infected_value > 50:
            return '#FED976'
        else:
            return '#FFEDA0'

def create_county_choropleth(event_data, timeline_value, view_type):
    """Create county-level map using individual county polygons to match React UI exactly"""
    
    if not event_data or timeline_value is None or timeline_value >= len(event_data):
        return create_empty_map()
    
    current_data = event_data[timeline_value]
    counties_data = current_data.get('counties', [])
    
    logger.info(f"Creating county map for day {current_data.get('day', 0)} with {len(counties_data)} counties")
    
    if not counties_data or not texas_geojson:
        return create_empty_map()
    
    # Create data mapping from FIPS to values
    county_values = {}
    county_info = {}
    
    for county in counties_data:
        fips = county.get('fips', '').strip()
        if not fips:
            continue
            
        # Ensure FIPS format matches GeoJSON geoid (48XXX format)
        if len(fips) == 3:
            full_fips = f"48{fips}"
        elif len(fips) == 5 and fips.startswith('48'):
            full_fips = fips
        else:
            full_fips = f"48{fips.zfill(3)}"
        
        if view_type == 'percent':
            value = county.get('infectedPercent', 0)
        else:
            value = county.get('infected', 0)
        
        county_values[full_fips] = value
        county_info[full_fips] = {
            'infected': county.get('infected', 0),
            'deceased': county.get('deceased', 0),
            'infectedPercent': county.get('infectedPercent', 0),
            'deceasedPercent': county.get('deceasedPercent', 0)
        }
        
        # Debug logging for first few counties
        if len(county_values) <= 3:
            logger.info(f"County {full_fips}: infected={county.get('infected', 0)}, percent={county.get('infectedPercent', 0)}")
    
    logger.info(f"Mapped {len(county_values)} counties to FIPS codes")
    
    # Get max value for color scale
    max_value = max(county_values.values()) if county_values.values() else 1
    if max_value == 0:
        max_value = 1
    
    # Define color function
    def get_color_from_value(value, max_val):
        if max_val == 0 or value == 0:
            return '#FFEDA0'
        
        ratio = value / max_val
        
        if ratio >= 1.0:
            return '#800026'
        elif ratio >= 0.75:
            return '#BD0026'
        elif ratio >= 0.625:
            return '#E31A1C'
        elif ratio >= 0.5:
            return '#FC4E2A'
        elif ratio >= 0.375:
            return '#FD8D3C'
        elif ratio >= 0.25:
            return '#FEB24C'
        elif ratio >= 0.125:
            return '#FED976'
        else:
            return '#FFEDA0'
    
    # Create figure with individual county shapes
    fig = go.Figure()
    
    # Add each county as a separate trace
    for feature in texas_geojson['features']:
        geoid = feature['properties']['geoid']
        county_name = feature['properties']['name']
        
        value = county_values.get(geoid, 0)
        color = get_color_from_value(value, max_value)
        
        info = county_info.get(geoid, {})
        infected = info.get('infected', 0)
        deceased = info.get('deceased', 0)
        infected_pct = info.get('infectedPercent', 0)
        deceased_pct = info.get('deceasedPercent', 0)
        
        # Extract coordinates for the county polygon
        coordinates = feature['geometry']['coordinates']
        
        # Handle MultiPolygon vs Polygon
        if feature['geometry']['type'] == 'MultiPolygon':
            for polygon in coordinates:
                for ring in polygon:
                    lons = [coord[0] for coord in ring]
                    lats = [coord[1] for coord in ring]
                    
                    fig.add_trace(go.Scatter(
                        x=lons,
                        y=lats,
                        fill='toself',
                        fillcolor=color,
                        line=dict(color='darkgray', width=0.5),
                        mode='lines',
                        name=county_name,
                        showlegend=False,
                        text=f'{county_name} County<br>Infected: {infected:,}<br>Deceased: {deceased:,}<br>Infected %: {infected_pct:.1f}%<br>Deceased %: {deceased_pct:.1f}%',
                        hoverinfo='text'
                    ))
        else:
            # Single Polygon
            for ring in coordinates:
                lons = [coord[0] for coord in ring]
                lats = [coord[1] for coord in ring]
                
                fig.add_trace(go.Scatter(
                    x=lons,
                    y=lats,
                    fill='toself',
                    fillcolor=color,
                    line=dict(color='darkgray', width=0.5),
                    mode='lines',
                    name=county_name,
                    showlegend=False,
                    text=f'{county_name} County<br>Infected: {infected:,}<br>Deceased: {deceased:,}<br>Infected %: {infected_pct:.1f}%<br>Deceased %: {deceased_pct:.1f}%',
                    hoverinfo='text'
                ))
    
    # Configure layout to match React version exactly
    fig.update_layout(
        title=f"Day {current_data.get('day', 0)} - Texas Counties ({'Percentage' if view_type == 'percent' else 'Count'} View)",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-106.0, -93.0]
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[25.0, 37.0],
            scaleanchor="x",
            scaleratio=1
        ),
        hovermode='closest'
    )
    
    logger.info("Successfully created county map with individual polygons")
    return fig

def create_empty_map():
    """Create empty map when no data is available"""
    fig = go.Figure()
    fig.update_layout(
        title="Texas Counties - No Data Available",
        geo=dict(
            scope='usa',
            projection=go.layout.geo.Projection(type='albers usa'),
            showframe=False,
            showcoastlines=False,
            showlakes=False,
            bgcolor='white',
            center=dict(lat=31.0, lon=-99.0),
            lonaxis_range=[-106.0, -93.0],
            lataxis_range=[25.0, 37.0]
        ),
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    return fig

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
                                className='dropdown-items',
                                n_clicks=0),
                            html.Button('Initial Cases',
                                id='initial-cases-btn',
                                className='dropdown-items',
                                n_clicks=0)
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
                                className='dropdown-items',
                                n_clicks=0),
                            html.Button('Antivirals',
                                id='antivirals-btn',
                                className='dropdown-items',
                                n_clicks=0),
                            html.Button('Vaccines',
                                id='vaccines-btn',
                                className='dropdown-items',
                                n_clicks=0)
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

# NPI (Non-Pharmaceutical Interventions) Modal Component
npi_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Non-Pharmaceutical Interventions")),
    dbc.ModalBody([
        html.Div([
            html.Label('NPI Name'),
            dcc.Input(id='npi-name', type='text', value='School Closures', 
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('NPI start (simulation day)'),
            dcc.Input(id='npi-start', type='number', value=5, min=0, max=1000, step=1,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('NPI duration (days)'),
            dcc.Input(id='npi-duration', type='number', value=30, min=1, max=1000, step=1,
                style={'width': '100%', 'marginBottom': '15px'})
        ]),
        
        # Age-specific effectiveness section
        html.Div([
            html.Label('NPI effectiveness (proportion)', style={'fontWeight': 'bold'}),
            html.Small('Age-specific effectiveness values', 
                style={'color': '#6c757d', 'display': 'block', 'marginBottom': '10px'}),
            
            html.Div([
                html.Label('0-4 years', style={'fontSize': '14px'}),
                dcc.Input(id='npi-eff-0-4', type='number', value=0.4, 
                    step=0.01, min=0, max=1,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('5-24 years', style={'fontSize': '14px'}),
                dcc.Input(id='npi-eff-5-24', type='number', value=0.35,
                    step=0.01, min=0, max=1,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('25-49 years', style={'fontSize': '14px'}),
                dcc.Input(id='npi-eff-25-49', type='number', value=0.2,
                    step=0.01, min=0, max=1,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('50-64 years', style={'fontSize': '14px'}),
                dcc.Input(id='npi-eff-50-64', type='number', value=0.25,
                    step=0.01, min=0, max=1,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('65+ years', style={'fontSize': '14px'}),
                dcc.Input(id='npi-eff-65-plus', type='number', value=0.1,
                    step=0.01, min=0, max=1,
                    style={'width': '100%', 'marginBottom': '15px'})
            ])
        ]),
        
        # Location selection
        html.Div([
            html.Label('Location'),
            dcc.Dropdown(
                id='npi-location',
                options=[{'label': 'Statewide', 'value': 'Statewide'}] + 
                        [{'label': county, 'value': county} for county in texas_counties],
                value='Statewide',
                multi=True,
                style={'marginBottom': '15px'}
            )
        ]),
        
        html.Button('Add NPI', id='add-npi-btn', 
            className='btn btn-secondary', style={'marginBottom': '15px'}),
        
        # Table showing added NPIs
        html.Div(id='npi-table')
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="npi-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="npi-close", className="ms-auto", n_clicks=0)
    ])
], id="npi-modal", is_open=False, size="lg")

# Antivirals Modal Component
antivirals_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Antivirals")),
    dbc.ModalBody([
        html.Div([
            html.Label('Antiviral Effectiveness'),
            dcc.Input(id='antiviral-effectiveness', type='number', value=0.15, 
                min=0, max=1, step=0.01,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Antiviral Wastage Factor (days)'),
            dcc.Input(id='antiviral-wastage', type='number', value=60, 
                min=0, max=1000, step=1,
                style={'width': '100%', 'marginBottom': '15px'})
        ]),
        
        html.H6('Stockpile Management', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        html.Div([
            html.Label('New Stockpile Day'),
            dcc.Input(id='antiviral-stockpile-day', type='number', value=50, 
                min=1, max=1000, step=1,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('New Stockpile Amount'),
            dcc.Input(id='antiviral-stockpile-amount', type='number', value=10000, 
                min=0, step=1,
                style={'width': '100%', 'marginBottom': '15px'})
        ])
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="antivirals-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="antivirals-close", className="ms-auto", n_clicks=0)
    ])
], id="antivirals-modal", is_open=False)

# Vaccines Modal Component
vaccines_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Vaccines")),
    dbc.ModalBody([
        html.Div([
            html.Label('Vaccine Effectiveness'),
            dcc.Input(id='vaccine-effectiveness', type='number', value=0.50, 
                min=0, max=1, step=0.01,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Vaccine Adherence'),
            dcc.Input(id='vaccine-adherence', type='number', value=0.50, 
                min=0, max=1, step=0.0001,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('Vaccine Wastage Factor (days)'),
            dcc.Input(id='vaccine-wastage', type='number', value=60, 
                min=0, max=1000, step=1,
                style={'width': '100%', 'marginBottom': '15px'})
        ]),
        
        # Vaccine Strategy
        html.Div([
            html.Label('Vaccine Strategy', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.RadioItems(
                id='vaccine-strategy',
                options=[
                    {'label': ' Pro Rata (distributes equally to all age groups)', 'value': 'pro_rata'},
                    {'label': ' Children (distributes to youngest age groups first)', 'value': 'children'}
                ],
                value='pro_rata',
                style={'marginBottom': '15px'}
            )
        ]),
        
        html.H6('Stockpile Management', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        html.Div([
            html.Label('New Stockpile Day'),
            dcc.Input(id='vaccine-stockpile-day', type='number', value=50, 
                min=1, max=1000, step=1,
                style={'width': '100%', 'marginBottom': '10px'})
        ]),
        html.Div([
            html.Label('New Stockpile Amount'),
            dcc.Input(id='vaccine-stockpile-amount', type='number', value=10000, 
                min=0, step=1,
                style={'width': '100%', 'marginBottom': '15px'})
        ])
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="vaccines-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="vaccines-close", className="ms-auto", n_clicks=0)
    ])
], id="vaccines-modal", is_open=False)

# Add modals to layout
app.layout.children.extend([disease_params_modal, initial_cases_modal, npi_modal, antivirals_modal, vaccines_modal])

# Navigation callback
@callback(
    [Output('main-content', 'children'),
     Output('nav-home', 'className'),
     Output('nav-userguide', 'className'),
     Output('disease-params-modal', 'is_open', allow_duplicate=True),
     Output('initial-cases-modal', 'is_open', allow_duplicate=True),
     Output('npi-modal', 'is_open', allow_duplicate=True),
     Output('antivirals-modal', 'is_open', allow_duplicate=True),
     Output('vaccines-modal', 'is_open', allow_duplicate=True)],
    [Input('nav-home', 'n_clicks'),
     Input('nav-userguide', 'n_clicks')],
    prevent_initial_call=True
)
def navigate_pages(home_clicks, userguide_clicks):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'nav-home'

    if triggered_id == 'nav-userguide':
        return create_userguide_layout(), 'tab-button', 'tab-button active', False, False, False, False, False
    else:
        return create_home_layout(), 'tab-button active', 'tab-button', False, False, False, False, False

# Initialize with home page
@callback(
    Output('main-content', 'children', allow_duplicate=True),
    Input('main-content', 'id'),
    prevent_initial_call='initial_duplicate'
)
def init_main_content(_):
    return create_home_layout()

# Restore UI state after navigation completes
@callback(
    [Output('play-pause-btn', 'disabled', allow_duplicate=True),
     Output('play-pause-btn', 'children', allow_duplicate=True),
     Output('play-pause-btn', 'style', allow_duplicate=True),
     Output('timeline-slider', 'disabled', allow_duplicate=True),
     Output('timeline-slider', 'max', allow_duplicate=True),
     Output('timeline-slider', 'value', allow_duplicate=True)],
    Input('main-content', 'children'),
    [State('simulation-state', 'data'),
     State('disease-parameters', 'data'),
     State('event-data', 'data')],
    prevent_initial_call=True
)
def restore_ui_after_navigation(content, sim_state, disease_params, event_data):
    """Restore play button and timeline after navigation creates new layout"""
    # Only restore if we're on the home page (has play button)
    # Check if content contains home layout by looking for play button
    if not content or not isinstance(content, dict):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Restore play button state
    has_disease_params = bool(disease_params)
    is_running = sim_state.get('isRunning', False)
    play_disabled = not has_disease_params

    if is_running:
        play_text = 'Pause'
        play_style = {
            'padding': '10px 30px',
            'fontSize': '16px',
            'backgroundColor': '#ffc107',
            'color': 'black',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'marginRight': '20px'
        }
    else:
        play_text = 'Play'
        play_style = {
            'padding': '10px 30px',
            'fontSize': '16px',
            'backgroundColor': '#28a745',
            'color': 'white',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'marginRight': '20px'
        }

    # Restore timeline state
    timeline_disabled = not bool(event_data)
    timeline_max = max(30, len(event_data)) if event_data else 30
    timeline_value = len(event_data) - 1 if event_data else 0

    logger.info(f"Restoring UI after navigation: play_disabled={play_disabled}, play_text={play_text}, timeline_value={timeline_value}")

    return play_disabled, play_text, play_style, timeline_disabled, timeline_max, timeline_value

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

# Modal toggle callbacks - Fixed to prevent auto-opening
@callback(
    Output('disease-params-modal', 'is_open'),
    [Input('disease-params-btn', 'n_clicks'),
     Input('disease-params-close', 'n_clicks'),
     Input('disease-params-save', 'n_clicks')],
    [State('disease-params-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_disease_params_modal(open_click, close_click, save_click, is_open):
    # Check which input triggered the callback
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Only toggle if the disease-params-btn was actually clicked (not just recreated)
    if triggered_id == 'disease-params-btn' and open_click:
        logger.info(f"Disease params button clicked: n_clicks={open_click}, current state={is_open}")
        return not is_open
    elif triggered_id in ['disease-params-close', 'disease-params-save'] and (close_click or save_click):
        return False

    # For any other case (like button recreation), preserve current state
    return dash.no_update

@callback(
    Output('initial-cases-modal', 'is_open'),
    [Input('initial-cases-btn', 'n_clicks'),
     Input('initial-cases-close', 'n_clicks'),
     Input('initial-cases-save', 'n_clicks')],
    [State('initial-cases-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_initial_cases_modal(open_click, close_click, save_click, is_open):
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'initial-cases-btn' and open_click:
        logger.info(f"Initial cases button clicked: n_clicks={open_click}, current state={is_open}")
        return not is_open
    elif triggered_id in ['initial-cases-close', 'initial-cases-save'] and (close_click or save_click):
        return False

    return dash.no_update

# Intervention modal toggle callbacks
@callback(
    Output('npi-modal', 'is_open'),
    [Input('npi-btn', 'n_clicks'),
     Input('npi-close', 'n_clicks'),
     Input('npi-save', 'n_clicks')],
    [State('npi-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_npi_modal(open_click, close_click, save_click, is_open):
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'npi-btn' and open_click:
        logger.info(f"NPI button clicked: n_clicks={open_click}, current state={is_open}")
        return not is_open
    elif triggered_id in ['npi-close', 'npi-save'] and (close_click or save_click):
        return False

    return dash.no_update

@callback(
    Output('antivirals-modal', 'is_open'),
    [Input('antivirals-btn', 'n_clicks'),
     Input('antivirals-close', 'n_clicks'),
     Input('antivirals-save', 'n_clicks')],
    [State('antivirals-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_antivirals_modal(open_click, close_click, save_click, is_open):
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'antivirals-btn' and open_click:
        logger.info(f"Antivirals button clicked: n_clicks={open_click}, current state={is_open}")
        return not is_open
    elif triggered_id in ['antivirals-close', 'antivirals-save'] and (close_click or save_click):
        return False

    return dash.no_update

@callback(
    Output('vaccines-modal', 'is_open'),
    [Input('vaccines-btn', 'n_clicks'),
     Input('vaccines-close', 'n_clicks'),
     Input('vaccines-save', 'n_clicks')],
    [State('vaccines-modal', 'is_open')],
    prevent_initial_call=True
)
def toggle_vaccines_modal(open_click, close_click, save_click, is_open):
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'vaccines-btn' and open_click:
        logger.info(f"Vaccines button clicked: n_clicks={open_click}, current state={is_open}")
        return not is_open
    elif triggered_id in ['vaccines-close', 'vaccines-save'] and (close_click or save_click):
        return False

    return dash.no_update

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
        
        # Enable play button if we have disease parameters (initial cases are optional in React)
        play_disabled = not bool(disease_params)
        
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

# Save intervention callbacks
@callback(
    [Output('npi-data', 'data'),
     Output('displayed-parameters-content', 'children', allow_duplicate=True)],
    Input('npi-save', 'n_clicks'),
    [State('npi-name', 'value'),
     State('npi-start', 'value'),
     State('npi-duration', 'value'),
     State('npi-eff-0-4', 'value'),
     State('npi-eff-5-24', 'value'),
     State('npi-eff-25-49', 'value'),
     State('npi-eff-50-64', 'value'),
     State('npi-eff-65-plus', 'value'),
     State('npi-location', 'value'),
     State('npi-data', 'data'),
     State('displayed-tab', 'data'),
     State('disease-parameters', 'data'),
     State('initial-cases-data', 'data'),
     State('antiviral-data', 'data'),
     State('vaccine-data', 'data')],
    prevent_initial_call=True
)
def save_npi(n_clicks, name, start, duration, eff_0_4, eff_5_24, eff_25_49, eff_50_64, eff_65_plus, 
             location, current_npi_data, displayed_tab, disease_params, initial_cases, antiviral_data, vaccine_data):
    if n_clicks:
        new_npi = {
            'name': name or 'School Closures',
            'start': start or 5,
            'duration': duration or 30,
            'effectiveness': [eff_0_4 or 0.4, eff_5_24 or 0.35, eff_25_49 or 0.2, eff_50_64 or 0.25, eff_65_plus or 0.1],
            'location': location or ['Statewide']
        }
        
        updated_npi_data = current_npi_data + [new_npi]
        
        # Update displayed content if on interventions tab
        if displayed_tab == 'interventions':
            content = create_interventions_display(updated_npi_data, antiviral_data, vaccine_data)
        else:
            content = create_scenario_display(disease_params, initial_cases)
        
        return updated_npi_data, content
    
    return dash.no_update, dash.no_update

@callback(
    [Output('antiviral-data', 'data'),
     Output('displayed-parameters-content', 'children', allow_duplicate=True)],
    Input('antivirals-save', 'n_clicks'),
    [State('antiviral-effectiveness', 'value'),
     State('antiviral-wastage', 'value'),
     State('antiviral-stockpile-day', 'value'),
     State('antiviral-stockpile-amount', 'value'),
     State('displayed-tab', 'data'),
     State('disease-parameters', 'data'),
     State('initial-cases-data', 'data'),
     State('npi-data', 'data'),
     State('vaccine-data', 'data')],
    prevent_initial_call=True
)
def save_antivirals(n_clicks, effectiveness, wastage, stockpile_day, stockpile_amount,
                   displayed_tab, disease_params, initial_cases, npi_data, vaccine_data):
    if n_clicks:
        antiviral_data = {
            'effectiveness': effectiveness or 0.15,
            'wastage_factor': wastage or 60,
            'stockpile_day': stockpile_day or 50,
            'stockpile_amount': stockpile_amount or 10000
        }
        
        # Update displayed content if on interventions tab
        if displayed_tab == 'interventions':
            content = create_interventions_display(npi_data, antiviral_data, vaccine_data)
        else:
            content = create_scenario_display(disease_params, initial_cases)
        
        return antiviral_data, content
    
    return dash.no_update, dash.no_update

@callback(
    [Output('vaccine-data', 'data'),
     Output('displayed-parameters-content', 'children', allow_duplicate=True)],
    Input('vaccines-save', 'n_clicks'),
    [State('vaccine-effectiveness', 'value'),
     State('vaccine-adherence', 'value'),
     State('vaccine-wastage', 'value'),
     State('vaccine-strategy', 'value'),
     State('vaccine-stockpile-day', 'value'),
     State('vaccine-stockpile-amount', 'value'),
     State('displayed-tab', 'data'),
     State('disease-parameters', 'data'),
     State('initial-cases-data', 'data'),
     State('npi-data', 'data'),
     State('antiviral-data', 'data')],
    prevent_initial_call=True
)
def save_vaccines(n_clicks, effectiveness, adherence, wastage, strategy, stockpile_day, stockpile_amount,
                 displayed_tab, disease_params, initial_cases, npi_data, antiviral_data):
    if n_clicks:
        vaccine_data = {
            'effectiveness': effectiveness or 0.50,
            'adherence': adherence or 0.50,
            'wastage_factor': wastage or 60,
            'strategy': strategy or 'pro_rata',
            'stockpile_day': stockpile_day or 50,
            'stockpile_amount': stockpile_amount or 10000
        }
        
        # Update displayed content if on interventions tab
        if displayed_tab == 'interventions':
            content = create_interventions_display(npi_data, antiviral_data, vaccine_data)
        else:
            content = create_scenario_display(disease_params, initial_cases)
        
        return vaccine_data, content
    
    return dash.no_update, dash.no_update

def create_interventions_display(npi_data, antiviral_data, vaccine_data):
    """Create interventions tab display content"""
    if not npi_data and not antiviral_data and not vaccine_data:
        return html.P('No interventions set yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})
    
    content = []
    
    # NPIs section
    if npi_data:
        content.extend([
            html.H6('Non-Pharmaceutical Interventions', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        ])
        for npi in npi_data:
            content.append(html.Div([
                html.P(f"Name: {npi['name']}"),
                html.P(f"Start Day: {npi['start']}, Duration: {npi['duration']} days"),
                html.P(f"Location: {', '.join(npi['location'])}"),
                html.P('Age-specific effectiveness:'),
                html.Ul([
                    html.Li(f"0-4: {npi['effectiveness'][0]:.2f}"),
                    html.Li(f"5-24: {npi['effectiveness'][1]:.2f}"),
                    html.Li(f"25-49: {npi['effectiveness'][2]:.2f}"),
                    html.Li(f"50-64: {npi['effectiveness'][3]:.2f}"),
                    html.Li(f"65+: {npi['effectiveness'][4]:.2f}")
                ], style={'marginLeft': '20px'})
            ], style={'marginBottom': '15px', 'padding': '10px', 'border': '1px solid #dee2e6', 'borderRadius': '4px'}))
    
    # Antivirals section
    if antiviral_data:
        content.extend([
            html.H6('Antivirals', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.P(f"Effectiveness: {antiviral_data['effectiveness']:.2f}"),
            html.P(f"Wastage Factor: {antiviral_data['wastage_factor']} days"),
            html.P(f"Stockpile: {antiviral_data['stockpile_amount']} on day {antiviral_data['stockpile_day']}")
        ])
    
    # Vaccines section
    if vaccine_data:
        strategy_label = 'Pro Rata' if vaccine_data['strategy'] == 'pro_rata' else 'Children First'
        content.extend([
            html.H6('Vaccines', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.P(f"Effectiveness: {vaccine_data['effectiveness']:.2f}"),
            html.P(f"Adherence: {vaccine_data['adherence']:.2f}"),
            html.P(f"Wastage Factor: {vaccine_data['wastage_factor']} days"),
            html.P(f"Strategy: {strategy_label}"),
            html.P(f"Stockpile: {vaccine_data['stockpile_amount']} on day {vaccine_data['stockpile_day']}")
        ])
    
    return html.Div(content)

# Play/Pause simulation callback - connects to Django backend
@callback(
    [Output('simulation-state', 'data'),
     Output('play-pause-btn', 'children'),
     Output('play-pause-btn', 'style'),
     Output('play-pause-btn', 'disabled', allow_duplicate=True),
     Output('simulation-interval', 'disabled'),
     Output('timeline-slider', 'disabled', allow_duplicate=True)],
    Input('play-pause-btn', 'n_clicks'),
    [State('simulation-state', 'data'),
     State('disease-parameters', 'data'),
     State('initial-cases-data', 'data'),
     State('npi-data', 'data'),
     State('antiviral-data', 'data'),
     State('vaccine-data', 'data')],
    prevent_initial_call=True
)
def toggle_simulation(n_clicks, sim_state, disease_params, initial_cases, npi_data, antiviral_data, vaccine_data):
    if n_clicks and disease_params:
        is_running = sim_state.get('isRunning', False)
        
        if not is_running:
            # Start simulation - call Django backend exactly like React
            try:
                logger.info("Starting new simulation...")
                # Format parameters for Django API exactly like React
                payload = {
                    'disease_name': disease_params.get('scenario_name', 'Custom'),
                    'R0': disease_params.get('R0', 1.2),
                    'beta_scale': disease_params.get('beta_scale', 10.0),
                    'tau': disease_params.get('tau', 1.2),
                    'kappa': disease_params.get('kappa', 1.9),
                    'gamma': disease_params.get('gamma', 4.1),
                    'chi': disease_params.get('chi', 1.0),
                    'rho': disease_params.get('rho', 0.39),
                    'nu': ','.join(map(str, disease_params.get('nu', [0,0,0,0,0])))
                }
                
                # Add default empty values for required fields
                payload.update({
                    'initial_infected': '[]',
                    'npis': '[]',
                    'antiviral_stockpile': 'null',
                    'antiviral_effectiveness': 0.8,
                    'antiviral_wastage_factor': 0.1,
                    'vaccine_stockpile': 'null',
                    'vaccine_effectiveness': 'null',
                    'vaccine_adherence': 'null',
                    'vaccine_wastage_factor': 0.1,
                    'vaccine_pro_rata': 1
                })
                
                # Add initial cases - use provided cases or default to Harris County
                initial_infected = []
                if initial_cases:
                    for case in initial_cases:
                        initial_infected.append({
                            'county': case['fips_id'],
                            'infected': case['cases'],
                            'age_group': case['age_group_id']
                        })
                else:
                    # Provide default initial case if none specified
                    initial_infected.append({
                        'county': '201',  # Harris County FIPS ID
                        'infected': 100,
                        'age_group': '0'  # 0-4 years age group
                    })
                payload['initial_infected'] = json.dumps(initial_infected)
                
                # Add interventions if any
                if npi_data:
                    npis = []
                    for npi in npi_data:
                        npis.append({
                            'type': npi['name'],
                            'start_day': npi['start'],
                            'duration': npi['duration'],
                            'effectiveness': npi['effectiveness'],
                            'location': npi['location']
                        })
                    payload['npis'] = json.dumps(npis)
                
                if antiviral_data:
                    payload.update({
                        'antiviral_effectiveness': antiviral_data['effectiveness'],
                        'antiviral_stockpile': antiviral_data['stockpile_amount'],
                        'antiviral_wastage_factor': antiviral_data['wastage_factor'] / 365.0  # Convert to proportion
                    })
                
                if vaccine_data:
                    payload.update({
                        'vaccine_effectiveness': vaccine_data['effectiveness'],
                        'vaccine_adherence': vaccine_data['adherence'],
                        'vaccine_stockpile': vaccine_data['stockpile_amount'],
                        'vaccine_wastage_factor': vaccine_data['wastage_factor'] / 365.0,  # Convert to proportion
                        'vaccine_pro_rata': vaccine_data['strategy']
                    })
                
                # Call Django API to create simulation
                logger.info(f"Sending payload to API: {payload}")
                response = requests.post(f'{API_BASE_URL}/api/pet/', json=payload)
                logger.info(f"API response status: {response.status_code}, content: {response.text}")
                if response.status_code == 201:
                    sim_id = response.json().get('id')
                    logger.info(f"Simulation created with ID: {sim_id}")
                    
                    # Start simulation
                    run_response = requests.get(f'{API_BASE_URL}/api/pet/{sim_id}/run')
                    logger.info(f"Run response status: {run_response.status_code}, content: {run_response.text}")
                    
                    if run_response.status_code in [200, 202]:
                        task_id = run_response.json().get('task_id')
                        logger.info(f"Simulation started with task ID: {task_id}")
                        
                        new_state = {
                            **sim_state, 
                            'isRunning': True, 
                            'currentIndex': 0,
                            'id': sim_id,
                            'taskId': task_id
                        }
                        
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
                    else:
                        logger.error(f"Failed to start simulation run: {run_response.status_code}")
                else:
                    logger.error(f"Failed to create simulation: {response.status_code}")
                
                # If API call failed, show error but don't start
                return sim_state, 'Play', dash.no_update, False, True, True

            except Exception as e:
                logger.error(f"Error starting simulation: {e}")
                return sim_state, 'Play', dash.no_update, False, True, True
        else:
            # Pause simulation - stop the task
            try:
                task_id = sim_state.get('taskId')
                if task_id:
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
            return new_state, 'Play', button_style, False, True, False

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Simulation data fetching callback - gets real data from Django backend
@callback(
    [Output('event-data', 'data'),
     Output('timeline-slider', 'max'),
     Output('timeline-slider', 'value')],
    Input('simulation-interval', 'n_intervals'),
    [State('simulation-state', 'data'),
     State('event-data', 'data')],
    prevent_initial_call=True
)
def fetch_simulation_data(n_intervals, sim_state, event_data):
    if sim_state.get('isRunning', False):
        current_day = len(event_data) + 1  # Start from day 1, not day 0
        
        try:
            # Fetch real data from Django backend
            logger.info(f"Fetching data for day {current_day}")
            response = requests.get(f'{API_BASE_URL}/api/output/{current_day}')
            logger.info(f"Output API response: {response.status_code}, content: {response.text[:200]}")
            
            if response.status_code == 200:
                api_data = response.json()
                
                # Convert Django response to React format
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
                
                # Extract county data and calculate totals - Django API returns counties as object with FIPS as keys
                total_S = total_E = total_A = total_T = total_I = total_R = total_D = 0
                
                # Handle the actual PES simulator format
                if 'total_summary' in api_data:
                    # Use the total_summary from PES simulator
                    total_summary = api_data['total_summary']
                    total_S = total_summary.get('S', 0)
                    total_E = total_summary.get('E', 0)
                    total_A = total_summary.get('A', 0)
                    total_T = total_summary.get('T', 0)
                    total_I = total_summary.get('I', 0)
                    total_R = total_summary.get('R', 0)
                    total_D = total_summary.get('D', 0)
                    
                    # Process county-level data from PES format
                    if 'data' in api_data:
                        for county_data in api_data['data']:
                            fips_id = county_data.get('fips_id', '')
                            compartment_summary = county_data.get('compartment_summary', {})
                            
                            infected = compartment_summary.get('I', 0)
                            deceased = compartment_summary.get('D', 0)
                            susceptible = compartment_summary.get('S', 0)
                            
                            # Calculate percentages
                            county_population = sum(compartment_summary.values()) if compartment_summary else 1
                            infected_percent = (infected / county_population * 100) if county_population > 0 else 0
                            deceased_percent = (deceased / county_population * 100) if county_population > 0 else 0
                            
                            county_info = {
                                'fips': fips_id,
                                'infected': infected,
                                'deceased': deceased,
                                'infectedPercent': infected_percent,
                                'deceasedPercent': deceased_percent
                            }
                            day_data['counties'].append(county_info)
                
                # Set calculated totals
                day_data.update({
                    'totalSusceptible': total_S,
                    'totalExposed': total_E,
                    'totalAsymptomaticCount': total_A,
                    'totalTreatableCount': total_T,
                    'totalInfectedCount': total_I,
                    'totalRecoveredCount': total_R,
                    'totalDeceased': total_D
                })
                
                updated_event_data = event_data + [day_data]
                logger.info(f"Added day {current_day} data, total days: {len(updated_event_data)}")
                return updated_event_data, len(updated_event_data), len(updated_event_data) - 1
            elif response.status_code == 404 or 'not calculated' in response.text:
                # Day not ready yet, don't increment but keep checking
                logger.info(f"Day {current_day} not ready yet")
                return event_data, max(30, len(event_data)), len(event_data) - 1 if event_data else 0
                
        except Exception as e:
            logger.error(f"API fetch failed: {e}")
    
    return event_data, max(30, len(event_data)), len(event_data) - 1 if event_data else 0

# Real data visualization callbacks
@callback(
    Output('spread-map', 'figure'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value')]
)
def update_map(event_data, timeline_value, view_type):
    """Update map with county-level choropleth visualization"""
    return create_county_choropleth(event_data, timeline_value, view_type)

@callback(
    Output('line-chart', 'figure'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value')]
)
def update_chart(event_data, timeline_value):
    if not event_data:
        fig = go.Figure()
        fig.update_layout(
            title="Epidemic Curve - No Data Available",
            xaxis_title="Day",
            yaxis_title="Population Count",
            height=300
        )
        return fig
    
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
        title=dict(
            text="Epidemic Curve - SEATIRD Model",
            y=0.98,
            yanchor='top'
        ),
        xaxis_title="Day",
        yaxis_title="Population Count",
        height=300,
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
        hovermode='x unified'
    )

    return fig

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
        # Map FIPS back to county name using GeoJSON data
        county_name = None
        
        # First try to get from GeoJSON data
        if texas_geojson:
            geoid = f"48{fips.zfill(3)}"
            for feature in texas_geojson['features']:
                if feature['properties']['geoid'] == geoid:
                    county_name = feature['properties']['name']
                    break
        
        # Fallback to mapping file
        if not county_name:
            for name, mapped_fips in texas_mapping.items():
                if mapped_fips == fips:
                    county_name = name
                    break
        
            # Handle different FIPS formats - the fips might be full 5-digit (48XXX) or just 3-digit (XXX)
        if len(fips) == 5 and fips.startswith('48'):
            # Full FIPS code like "48419"
            geoid = fips
            short_fips = fips[2:]  # Remove "48" prefix for mapping lookup
        elif len(fips) == 3:
            # 3-digit FIPS code like "419"
            geoid = f"48{fips}"
            short_fips = fips
        else:
            # Handle other formats
            geoid = f"48{fips.zfill(3)}"
            short_fips = fips.zfill(3)

     
        if texas_geojson:
            for feature in texas_geojson['features']:
                if feature['properties']['geoid'] == geoid:
                    county_name = feature['properties']['name']
                    break

        # Fallback to mapping file using short FIPS
        if not county_name:
            # Remove leading zeros from short_fips for comparison
            short_fips_no_zero = short_fips.lstrip('0')
            for name, mapped_fips in texas_mapping.items():
                if mapped_fips == short_fips_no_zero:
                    county_name = name
                    break

        # Final fallback - show readable county name instead of number
        if not county_name:
            county_name = f"County {short_fips}"
        
        if view_type == 'percent':
            infected_val = f"{county.get('infectedPercent', 0):.1f}%"
            deceased_val = f"{county.get('deceasedPercent', 0):.1f}%"
        else:
            infected_val = f"{county.get('infected', 0):,}"
            deceased_val = f"{county.get('deceased', 0):,}"
        
        table_data.append([county_name, infected_val, deceased_val])
    
    # Create table
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th('County'),
                html.Th('Infected'),
                html.Th('Deceased')
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(row[0]),
                html.Td(row[1]),
                html.Td(row[2])
            ]) for row in table_data
        ])
    ],   
        bordered=True,
        hover=True,
        striped=True,
        responsive=False,
        className="w-100",
        style= {
            'maxHeight': '800px',
            'overflowY': 'auto',
            'display': 'block'
        }
    ), 

    return table

# Expose server for deployment
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8051)
                   