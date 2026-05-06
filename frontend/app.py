import glob
import json
import logging
import math
import os
import subprocess

import dash
from dash import dcc, html, Input, Output, State, callback, ctx, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import requests

from user_guide import create_userguide_layout


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get version from environment
result = subprocess.run("git symbolic-ref -q --short HEAD || git describe --tags --exact-match",
                        shell=True, capture_output=True)
version = result.stdout.decode("utf-8").strip() if result.stdout else 'Unknown'

# Initialize Dash app with external CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = f'epiENGAGE - Interactive Outbreak Simulator v-{version}'
app.config.suppress_callback_exceptions = True

# API Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://django-backend:8000')

# Dirs with spatial data (names and polygons)
ASSETS_DIR = 'assets'
NAME_DIR = os.path.join(ASSETS_DIR, 'fips_to_names')
GEO_DIR  = os.path.join(ASSETS_DIR, 'map_boundaries')


# ============================================================================
# MODEL OPTIONS
# ============================================================================
MODEL_OPTIONS = [
    {
        'label': 'SEIRS Deterministic',
        'value': 'seirs-deterministic',
        'description': 'SEIR with waning immunity; Euler updates; fractional flows; stochastic binomial travel.'
    },
    {
        'label': 'SEIRS Stochastic',
        'value': 'seirs-stochastic',
        'description': 'SEIR with waning immunity; Poisson transitions; stochastic binomial travel.'
    },
    {
        'label': 'SEATIRD Deterministic',
        'value': 'seatird-deterministic',
        'description': 'Adds treatable compartment; Euler updates (fractional flows); stochastic binomial travel.'
    },
    {
        'label': 'SEATIRD Stochastic',
        'value': 'seatird-stochastic',
        'description': 'SEATIRD with exponential transitions (Gillespie, individual-level stochasticity); stochastic binomial travel.'
    },
#    {
#        'label': 'SEIHRD Stochastic',
#        'value': 'seihrd-deterministic',
#        'description': 'Adds hospitalization and death; Poisson transitions; stochastic binomial travel.'
#    },
]

# Preset scenarios
PRESET_SCENARIOS = {
    'seatird': {
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
    },
    'seirs': {
        'slow_transmission': {
                'name': 'Slow Transmission',
                'disease_name': 'Slow Transmission',
                'R0': 1.2,
                'latent_period': 1,
                'infectious_period': 7,
                'immune_period': 0,
            },
        'fast_transmission': {
            'name': 'Fast Transmission',
            'disease_name': 'Fast Transmission',
            'R0': 2.5,
            'latent_period': 1,
            'infectious_period': 7,
            'immune_period': 0,
        }
    }
}


# ============================================================================
# STATE OPTIONS
# ============================================================================

# Collect prefixes from each directory
def _get_prefix(fn):
    return os.path.splitext(fn)[0].split('_', 1)[0]


def _build_jurisdiction_options(mapping_dir: str, boundaries_dir: str, require_both: bool):
    """
    Returns options like [{"label": "...", "value": "..."}] for jurisdictions
    that have the required assets.
    - value: prefix before first "_" in the filename
    - label: known mapping else hyphens -> spaces
    """
    mapping_prefixes = {
        _get_prefix(f) for f in os.listdir(mapping_dir)
        if f.endswith(".json")
    }

    boundary_prefixes = {
        _get_prefix(f) for f in os.listdir(boundaries_dir)
        if f.endswith(".geojson")
    }

    prefixes = (
        mapping_prefixes & boundary_prefixes
        if require_both else
        mapping_prefixes | boundary_prefixes
    )

    options = []
    for value in sorted(prefixes):
        label = value.replace("-", " ") # US_JURISDICTION_LABELS.get(value,
        options.append({"label": label, "value": value})

    return options

STATE_OPTIONS = _build_jurisdiction_options(NAME_DIR, GEO_DIR, require_both=True)


# ============================================================================
# OTHER OPTIONS
# ============================================================================

# Age group constants
AGE_GROUPS = [
    {'value': '0-4 years', 'label': '0-4 years'},
    {'value': '5-17 years', 'label': '5-17 years'},
    {'value': '18-49 years', 'label': '18-49 years'},
    {'value': '50-64 years', 'label': '50-64 years'},
    {'value': '65+ years', 'label': '65+ years'}
]

AGE_GROUP_MAPPING = {
    '0-4 years': '0',
    '5-17 years': '1', 
    '18-49 years': '2',
    '50-64 years': '3',
    '65+ years': '4'
}



# ============================================================================
# HELPER FUNCTIONS FOR MAPS
# ============================================================================

def _first_match(pattern: str):
    """Load location jurisdiction node names and boundaries from subdirs"""
    matches = sorted(glob.glob(pattern))
    return matches[0] if matches else None


def _load_location_assets(location_value: str):
    """
    Load all assets needed to plot a location.

    Required:
      - assets/fips_to_names/{value}_*.json
      - assets/map_boundaries/{value}_*.geojson

    Returns:
      names   : list[str]   (derived from mapping keys, excluding "All")
      mapping : dict[str,str]
      geojson : dict
    """
    # ---- name -> id mapping (required)
    name_path = _first_match(os.path.join(NAME_DIR, f"{location_value}_*.json"))
    if not name_path:
        raise FileNotFoundError(
            f"Missing name mapping for '{location_value}'. "
            f"Expected {NAME_DIR}/{location_value}_*.json"
        )

    with open(name_path, "r") as f:
        mapping = json.load(f)

    names = [k for k in mapping.keys() if k.lower() != "all"]

    # ---- geometry (required)
    geo_path = (
        _first_match(os.path.join(GEO_DIR, f"{location_value}_*.geojson"))
        or _first_match(os.path.join(GEO_DIR, f"{location_value}_*.json"))
    )
    if not geo_path:
        raise FileNotFoundError(
            f"Missing geometry for '{location_value}'. "
            f"Expected {GEO_DIR}/{location_value}_*.geojson (or .json)"
        )

    with open(geo_path, "r") as f:
        geojson = json.load(f)

    return names, mapping, geojson


def _create_empty_map():
    """Create empty map when no data is available"""
    fig = go.Figure()
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title="Map - No Data Available"
    )
    return fig

def _create_empty_state_map(geojson):
    """Create map showing state boundaries before simulation starts"""
    if not geojson or 'features' not in geojson:
        return _create_empty_map()
    
    fig = go.Figure()
    
    # Add each county as a light yellow shape with boundary
    for feature in geojson['features']:
        county_name = feature['properties'].get('NAME', 'Unknown')
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
                        fillcolor='#FFEDA0',  # Light yellow
                        line=dict(color='darkgray', width=0.5),
                        mode='lines',
                        name=county_name,
                        showlegend=False,
                        text=f'{county_name} - No data yet - click PLAY to start simulation',
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
                    fillcolor='#FFEDA0',  # Light yellow
                    line=dict(color='darkgray', width=0.5),
                    mode='lines',
                    name=county_name,
                    showlegend=False,
                    text=f'{county_name} - No data yet - click PLAY to start simulation',
                    hoverinfo='text'
                ))
    
    fig.update_layout(
        title="Map - No Data Available (Select disease parameters and click PLAY)",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, scaleanchor="x", scaleratio=1),
        hovermode='closest'
    )
    
    fig.update_xaxes(autorange=True)
    fig.update_yaxes(autorange=True)
    
    return fig


def _get_color_from_value(value, max_val):
    """Define color function"""
    if max_val == 0 or value == 0:
        return '#FFEDA0'
    ratio = math.log1p(value) / math.log1p(max_val)
    
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
    else:
        return '#FED976'


def _create_jurisdiction_choropleth(event_data, timeline_value, view_type, geojson, selected_model):
    """Create map using boundary file provided in geojson"""    
    if not event_data or timeline_value is None or timeline_value >= len(event_data):
        return _create_empty_map()
    
    current_data = event_data[timeline_value]
    counties_data = current_data.get('counties', [])
    
    logger.info(f"Creating county map for day {current_data.get('day', 0)} with {len(counties_data)} counties")
    
    if not counties_data or not geojson:
        return _create_empty_map()
    
    # Create data mapping from FIPS to values
    county_values = {}
    county_info = {}
    
    for county in counties_data:
        fips = county.get('fips', '').strip()
        if not fips:
            continue
            
        # Ensure FIPS format matches GeoJSON geoid (48XXX format)
        # Older versions of code allowed 3 char fips of county only
        if len(fips) == 3:
            full_fips = f"48{fips}"
        elif len(fips) == 4: # Leading 0s of states are getting lost
            full_fips = fips.zfill(5)
        else:
            full_fips = fips
        
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
            logger.info(f"County {full_fips}: Infectious={county.get('infected', 0)}, percent={county.get('infectedPercent', 0)}")
    
    logger.info(f"Mapped {len(county_values)} counties to FIPS codes")
    
    # Get max value for color scale
    max_value = max(county_values.values()) if county_values.values() else 1
    if max_value == 0:
        max_value = 1
    
    # Create figure with individual county shapes
    fig = go.Figure()
    
    # Add each county as a separate trace
    for feature in geojson['features']:
        geoid = feature['properties']['GEOID']
        county_name = feature['properties']['NAMELSAD']
        
        value = county_values.get(geoid, 0)
        color = _get_color_from_value(value, max_value)
        
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

                    model = (selected_model or "").lower()
                    if model.startswith("seir") or model.startswith("seirs"):
                        fig.add_trace(go.Scatter(
                            x=lons,
                            y=lats,
                            fill='toself',
                            fillcolor=color,
                            line=dict(color='darkgray', width=0.5),
                            mode='lines',
                            name=county_name,
                            showlegend=False,
                            text=f'{county_name}<br>Infectious: {infected:,} ({infected_pct:.1f}%)<br>Recovered: {deceased:,} ({deceased_pct:.1f}%)',
                            hoverinfo='text'
                        ))
                    else:
                        fig.add_trace(go.Scatter(
                            x=lons,
                            y=lats,
                            fill='toself',
                            fillcolor=color,
                            line=dict(color='darkgray', width=0.5),
                            mode='lines',
                            name=county_name,
                            showlegend=False,
                            text=f'{county_name}<br>Infectious: {infected:,} ({infected_pct:.1f}%)<br>Deceased: {deceased:,} ({deceased_pct:.1f}%)',
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
                    text=f'{county_name} County<br>Infectious: {infected:,} ({infected_pct:.1f}%)<br>Deceased: {deceased:,} ({deceased_pct:.1f}%)',
                    hoverinfo='text'
                ))
    
    # Configure layout to match React version exactly
    fig.update_layout(
        title=f"Day {current_data.get('day', 0)} ({'Percentage' if view_type == 'percent' else 'Count'} View)",
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, scaleanchor="x", scaleratio=1),
        hovermode='closest'
    )

    fig.update_xaxes(autorange=True)
    fig.update_yaxes(autorange=True)
    
    logger.info("Successfully created county map with individual polygons")
    return fig


# ============================================================================
# APP LAYOUT
# ============================================================================
app.layout = html.Div([
    # Stores for state management
    dcc.Store(id='simulation-state', data={'isRunning': False, 'currentIndex': 0, 'taskId': None, 'id': None}),
    dcc.Store(id='event-data', data=[]),
    dcc.Store(id='view-type', data='count'),
    dcc.Store(id='disease-parameters', data={}),
    dcc.Store(id='initial-cases-data', data=[]),
    dcc.Store(id='npi-data', data=[]),
    dcc.Store(id='antiviral-data', data={}),
    dcc.Store(id='vaccine-data', data={}),
    dcc.Store(id='vaccine-stockpile', data=[]),
    dcc.Store(id='antivirals-enabled', data=False),
    dcc.Store(id='vaccines-enabled', data=False),
    dcc.Store(id='displayed-tab', data='scenario'),
    dcc.Interval(id='simulation-interval', interval=1000, disabled=True),
    
    # Stores for Model and State Selection
    dcc.Store(id='selected-model-store', data='seirs-deterministic'),
    dcc.Store(id='selected-state-store', data='Alabama'),
    dcc.Store(id='location-assets-store', data={}),
    
    # Header
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
                        'marginLeft': '10px',
                        'marginRight': '20px'
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
                    html.Span(f'Interactive Outbreak Simulator v-{version}', style={'color': 'white'})
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

# ============================================================================
# FUNCTIONS TO CREATE ELEMENTS FOR MAIN CONTENT AREA
# ============================================================================
def create_model_state_selection_panel():
    """
    Creates the Model and State selection dropdowns.
    This is the core UI for Features 1 and 2.
    """
    return html.Div([
        # Panel Header
        html.Div([
            html.H6('Simulation Setup', style={
                'marginBottom': '15px',
                'paddingBottom': '10px',
                'borderBottom': '2px solid #102c41',
                'color': '#102c41',
                'fontWeight': 'bold'
            })
        ]),
        
        # FEATURE 1: Model Selection Dropdown
        html.Div([
            html.Label('Disease Model', style={
                'fontWeight': 'bold',
                'marginBottom': '5px',
                'display': 'block',
                'color': '#333'
            }),
            dcc.Dropdown(
                id='model-selector-dropdown',
                options=[{"label": m["label"], "value": m["value"]} for m in MODEL_OPTIONS],
                value='seirs-deterministic',
                clearable=True,
                placeholder="Select a disease model...",
                style={'marginBottom': '8px'}
            ),
            # Model description display
            html.Div(
                id='model-description-display',
                style={
                    'fontSize': '12px',
                    'color': '#666',
                    'padding': '8px',
                    'backgroundColor': '#f8f9fa',
                    'borderRadius': '4px',
                    'marginBottom': '15px'
                }
            )
        ]),
        
        # FEATURE 2: State Selection Dropdown
        html.Div([
            html.Label('State', style={
                'fontWeight': 'bold',
                'marginBottom': '5px',
                'display': 'block',
                'color': '#333'
            }),
            dcc.Dropdown(
                id='state-selector-dropdown',
                options=[{"label": s["label"], "value": s["value"]} for s in STATE_OPTIONS],
                value='Alabama',
                clearable=True,
                searchable=True,
                placeholder="Select a state...",
                style={'marginBottom': '15px'}
            ),
        ]),
        
        # Apply Button
        html.Button(
            '✓ Apply Selection',
            id='apply-model-state-btn',
            n_clicks=0,
            style={
                'width': '100%',
                'padding': '10px',
                'backgroundColor': '#102c41',
                'color': 'white',
                'border': 'none',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'marginBottom': '10px'
            }
        ),
        
        # Status message area
        html.Div(id='model-state-status-message', style={'marginBottom': '15px'})
    ], style={
        'padding': '15px',
        'backgroundColor': 'white',
        'borderRadius': '8px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'marginBottom': '15px'
    })


# Home page layout
def create_home_layout():
    return html.Div([
        # Main content row with fixed height
        html.Div([
            # Left Panel - Settings
            html.Div([
                html.Div([
                    # Model and State Selection Panel
                    create_model_state_selection_panel(),
                    
                    # Set Scenario dropdown
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
                    
                    # Interventions dropdown 
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
                                n_clicks=0,
                                style={'display': 'none'}), ### Remove this style to show Antiviral button ###
                            html.Button('Vaccines',
                                id='vaccines-btn',
                                className='dropdown-items',
                                n_clicks=0)
                        ],
                        id='interventions-dropdown',
                        style={'display': 'none'})
                    ], style={'position': 'relative', 'marginBottom': '10px'}),
                    
                    # DisplayedParameters section 
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
                ], className='left-panel', style={
                    'height': '100%',
                    'overflowY': 'auto',
                    'overflowX': 'hidden',
                    'paddingRight': '10px',
                })
            ], className='col-lg-2', style={
                'flex': '0 0 20%',
                'maxWidth': '20%',
                'height': '100%',        # inherit from row
                'minHeight': 0,
                'overflowY': 'auto',
            }),

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
                        value='count',
                        inline=True,
                        labelStyle={'marginRight': '20px'},
                        style={'marginBottom': '15px', 'paddingLeft': '10px'}
                    )
                ], className='top-middle-panel'),

                # Map and Chart container
                html.Div([
                    # Map
                    dcc.Graph(
                        id='spread-map',
                        style={'flex': '0 0 400px'},
                        config={'displayModeBar': False}
                    ),

                    # Line Chart
                    dcc.Graph(
                        id='line-chart',
                        style={'flex': '1 1 auto'},
                        config={'displayModeBar': False}
                    )
                ],
                className='map-and-chart-container',
                style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'height': '100%',
                    'minHeight': 0,
                    'overflow': 'hidden'
                })
            ], className='col-lg-7', style={
                'flex': '0 0 58%',
                'maxWidth': '58%',
                'height': '100%',
                'minHeight': 0
            }),
            
            # Right Panel - Table
            html.Div([
                html.Div([
                    html.H6('County Data', style={'marginBottom': '10px'}),
                    dcc.Input(
                        id='county-search',
                        type='text',
                        placeholder='Search (county or number)…',
                        debounce=True,
                        style={'width': '100%', 'marginBottom': '10px'}
                    ),
                    dcc.Store(id='county-table-sort', data={'col': 'infected', 'dir': 'desc'}),
                    html.Button(id='sort-location', n_clicks=0, style={'display': 'none'}),
                    html.Button(id='sort-infected', n_clicks=0, style={'display': 'none'}),
                    html.Button(id='sort-deceased', n_clicks=0, style={'display': 'none'}),
                    html.Div(id='spread-table', style={'flex': '1 1 auto', 'minHeight': 0, 'overflowY': 'auto'})
                ], className='right-panel', style={
                    'height': '100%', 'minHeight': 0,
                    'display': 'flex', 'flexDirection': 'column', 'overflow': 'hidden'})
            ], className='col-lg-3', style={
                'flex': '0 0 22%',
                'maxWidth': '22%',
                'height': '100%',
                'minHeight': 0
            }),
        ], className='row', style={
            'display': 'flex',
            'height': 'calc(100vh - 80px)',  # subtract fixed header (80px)
            'paddingBottom': '70px', # reserve fixed footer height
            'boxSizing': 'border-box',
            'overflow': 'hidden',
        }),
        
        # Footer - OUTSIDE the row, always visible at bottom
        html.Div([
            html.Div([
                # Reset Button
                html.A(html.Button(
                    'Reset',
                    id='reset-btn',
                    disabled=False,
                    className='reset-button',
                ), href='/'),

                # Play/Pause Button
                html.Button(
                    'Play',
                    id='play-pause-btn',
                    disabled=True,
                    className='play-pause-button',
                    style={
                        'padding': '10px 30px',
                        'fontSize': '16px',
                        'backgroundColor': '#28a745',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'marginRight': '20px',
                    }
                ),
                
                # Timeline Slider
                html.Div([
                    dcc.Slider(
                        id='timeline-slider',
                        min=0,
                        step=1,
                        value=0,
                        marks={i: str(i) for i in range(0, 201, 5)},
                        tooltip={'placement': 'bottom', 'always_visible': True},
                        disabled=True
                    )
                ], style={'width': '60%', 'display': 'inline-block', 'verticalAlign': 'middle'})
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'flex-start',
                'padding': '15px 20px',
            })
        ], style={
            'position': 'fixed',
            'bottom': '0',
            'left': '0',
            'right': '0',
            'backgroundColor': 'white',
            'borderTop': '1px solid #dee2e6',
            'zIndex': '999',
            'height': '70px',
        })
    ])


# ============================================================================
# MODALS
# ============================================================================
# Disease Parameters Modal Component
disease_params_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Disease Parameters")),
    dbc.ModalBody(id="disease-params-modal-body"),
    dbc.ModalFooter([
        dbc.Button("Save", id="disease-params-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="disease-params-close", className="ms-auto", n_clicks=0)
    ])
], id="disease-params-modal", is_open=False, size="lg")


@callback(
    Output('disease-params-modal-body', 'children'),
    Input('model-selector-dropdown', 'value'),
    prevent_initial_call=True
)
def update_disease_param_modal_body(selected_value):
    scenario_prefix = selected_value.split('-')[0]

    if selected_value is not None:
        return dbc.ModalBody([
            # Preset scenarios dropdown
            html.Div([
                html.Label('Load from Catalog', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id='preset-scenario-dropdown',
                    options=[
                        {'label': scenario['name'], 'value': key} 
                        for key, scenario in PRESET_SCENARIOS[scenario_prefix].items()
                    ],
                    placeholder='Select a preset scenario...',
                    style={'marginBottom': '15px'}
                )
            ]),
            
            html.Hr(),
            
            # Currently all models expect scenario name, R0, and latent period
            html.Div([
                html.Label('Scenario Name', style={'fontWeight': 'bold'}),
                dcc.Input(id='scenario-name', type='text', value='', 
                    style={'width': '100%', 'marginBottom': '10px'})
            ]),
            html.Div([
                html.Label('Reproduction Number (R₀)', style={'fontWeight': 'bold'}),
                html.Small(' - Average number of secondary infections in a susceptible population', 
                    style={'color': '#6c757d'}),
                dcc.Input(id='reproduction-number', type='number', value=1.2, step=0.1, min=0,
                    style={'width': '100%', 'marginBottom': '10px'})
            ]),
    
            html.Div([
                html.Label('Latent period (days)', style={'fontWeight': 'bold'}),
                html.Small(' - Average number of days from infection to infectiousness',
                    style={'color': '#6c757d'}),
                dcc.Input(id='latent-period', type='number', value=1.2, step=0.1, min=0,
                    style={'width': '100%', 'marginBottom': '10px'})
            ]),
    
            # Asymptomatic, symptomatic, CFR and sigma just for SEATIRD
            html.Div([
                html.Label('Asymptomatic period (days)', style={'fontWeight': 'bold'}),
                html.Small(' - Average number of days spent infectious, but not yet symptomatic',
                    style={'color': '#6c757d'}),
                dcc.Input(id='asymptomatic-period', type='number', value=1.9, step=0.1, min=0,
                    style={'width': '100%', 'marginBottom': '10px'})
            ], id='disease-param-modal-display-asymptomatic', style={'display': 'none'}),
            html.Div([
                html.Label('Symptomatic period (days)', style={'fontWeight': 'bold'}),
                html.Small(' - Average number of days spent symptomatic and infectious',
                    style={'color': '#6c757d'}),
                dcc.Input(id='symptomatic-period', type='number', value=4.1, step=0.1, min=0,
                    style={'width': '100%', 'marginBottom': '15px'})
            ], id='disease-param-modal-display-symptomatic', style={'display': 'none'}),

            # Age-specific CFR section => this is not CFR in the model it's mean time to death
            html.Div([
                html.Label('Mortality rate (1/days)', style={'fontWeight': 'bold'}),
                html.Small(' - Inverse average number of days spent asymptomatic/treatable/infectious to deceased',
                    style={'color': '#6c757d', 'display': 'block', 'marginBottom': '15px'}),
                
                # CFR inputs for each age group
                html.Div([
                    html.Label('0-4 years', style={'fontSize': '14px'}),
                    dcc.Input(id='cfr-0-4', type='number', value=0.000022319, 
                        step=0.000000001, min=0, max=100,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('5-17 years', style={'fontSize': '14px'}),
                    dcc.Input(id='cfr-5-24', type='number', value=0.000040975,
                        step=0.000000001, min=0, max=100,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('18-49 years', style={'fontSize': '14px'}),
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
                        style={'width': '100%', 'marginBottom': '25px'})
                ])
            ], id='disease-param-modal-display-cfr', style={'display': 'none'}),
    
            # Age-specific relative susceptibility section
            html.Div([
                html.Label('Relative susceptibility (ratio)', style={'fontWeight': 'bold'}),
                html.Small(' - How susceptible each age group is relative to a reference group (e.g. 0-4yro)',
                    style={'color': '#6c757d', 'display': 'block', 'marginBottom': '15px'}),
                
                # inputs for each age group
                html.Div([
                    html.Label('0-4 years', style={'fontSize': '14px'}),
                    dcc.Input(id='sigma-0-4', type='number', value=1.0, 
                        step=0.000000001, min=0, max=10,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('5-17 years', style={'fontSize': '14px'}),
                    dcc.Input(id='sigma-5-24', type='number', value=1.0,
                        step=0.000000001, min=0, max=10,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('18-49 years', style={'fontSize': '14px'}),
                    dcc.Input(id='sigma-25-49', type='number', value=1.0,
                        step=0.000000001, min=0, max=10,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('50-64 years', style={'fontSize': '14px'}),
                    dcc.Input(id='sigma-50-64', type='number', value=1.0,
                        step=0.000000001, min=0, max=10,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('65+ years', style={'fontSize': '14px'}),
                    dcc.Input(id='sigma-65-plus', type='number', value=1.0,
                        step=0.000000001, min=0, max=10,
                        style={'width': '100%', 'marginBottom': '5px'})
                ])
            ], id='disease-param-modal-display-sigma', style={'display': 'none'}),

            # These next two just for SEIRS
            html.Div([
                html.Label('Infectious period (days)', style={'fontWeight': 'bold'}),
                html.Small(' - Average number of days spent infectious',
                    style={'color': '#6c757d'}),
                dcc.Input(id='infectious-period', type='number', value=1.9, step=0.1, min=0,
                    style={'width': '100%', 'marginBottom': '10px'})
            ], id='disease-param-modal-display-infectious', style={'display': 'none'}),
            html.Div([
                html.Label('Immune period (days)', style={'fontWeight': 'bold'}),
                html.Small(' - Average number of days before returning to susceptible (set to 0 to make this an SEIR model)',
                    style={'color': '#6c757d'}),
                dcc.Input(id='immune-period', type='number', value=0, step=0.1, min=0,
                    style={'width': '100%', 'marginBottom': '15px'})
            ], id='disease-param-modal-display-immune', style={'display': 'none'})
        ])
    else:
        return dbc.ModalBody(['Select a valid disease model to set parameters.'])



# Initial Cases Modal Component  
initial_cases_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Initial Cases")),
    dbc.ModalBody([
        html.Div([
            html.Label('Location'),
            dcc.Dropdown(
                id='initial-location',
                options=[],
                placeholder='Search for a location...',
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
                value='18-49 years',
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
                html.Label('5-17 years', style={'fontSize': '14px'}),
                dcc.Input(id='npi-eff-5-24', type='number', value=0.35,
                    step=0.01, min=0, max=1,
                    style={'width': '100%', 'marginBottom': '5px'})
            ]),
            html.Div([
                html.Label('18-49 years', style={'fontSize': '14px'}),
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
                options=[],
                value=['Statewide'],
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


VACCINE_MODELS = {
    "stockpile-age-risk": "Stockpile Release by Age", # Currently doesn't allow for risk preference
}

# Vaccines Modal Component
vaccines_modal = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Vaccines")),

    dbc.ModalBody([
        html.Div([
            html.Label('Vaccine Model', style={'fontWeight': 'bold', 'marginBottom': '5px'}),
            dcc.Dropdown(
                options=[
                    {'label': model, 'value': key}
                    for key, model in VACCINE_MODELS.items()
                ],
                placeholder='Select a vaccine model...',
                clearable=True,
                style={'marginBottom': '15px'},
                id='vaccine-model-dropdown',
            )
        ]),
        html.Hr(),
        html.Div(id='vaccine-parameter-body'),
    ]),
    dbc.ModalFooter([
        dbc.Button("Save", id="vaccines-save", className="ms-auto", n_clicks=0),
        dbc.Button("Close", id="vaccines-close", className="ms-auto", n_clicks=0)
    ])
], id="vaccines-modal", is_open=False)


@callback(
    Output('vaccine-parameter-body', 'children'),
    Input('vaccine-model-dropdown', 'value'),
    prevent_initial_call=True
)
def update_vaccines_modal_body(selected_value):
    if selected_value == 'stockpile-age-risk':
        return html.Div([

            # Vaccine priority groups
            html.Div([
                html.Label('Vaccine Priority Groups', style={'fontWeight': 'bold'}),
                html.Small('Select age specific priority groups for vaccine distribution',
                    style={'color': '#6c757d', 'display': 'block', 'marginBottom': '10px'}),

                dcc.Checklist(
                    id='vaccine-age-risk-priority-groups',
                    options=[
                        { 'label': '0-4 years', 'value': 'vac-arpg-0-4' },
                        { 'label': '5-17 years', 'value': 'vac-arpg-5-17' },
                        { 'label': '18-49 years', 'value': 'vac-arpg-18-49' },
                        { 'label': '50-64 years', 'value': 'vac-arpg-50-64' },
                        { 'label': '65+ years', 'value': 'vac-arpg-65-plus' },
                    ], value=['vac-arpg-18-49'],
                    inputStyle={'marginRight': '10px'},
                    labelStyle={'display': 'flex', 'align-items': 'center', 'fontSize': '14px'},
                ),
            ], style={'marginBottom': '15px'}),

            html.Div([
                html.Label('Vaccine Half Life (days)', style={'fontWeight': 'bold'}),
                html.Small('Number of days required to clear half the vaccine from the body'),
                dcc.Input(id='vaccine-half-life', type='number', value=60,
                    min=0, max=1000, step=1,
                    style={'width': '100%', 'marginBottom': '15px'})
            ], style={'display': 'none'}), ### This is currently hidden ###

            html.Div([
                html.Label('Vaccine Capacity (proportion)', style={'fontWeight': 'bold'}),
                html.Small('Proportion of population the jurisdiction has the capacity to vaccinate per day, from 0 to 1'),
                dcc.Input(id='vaccine-capacity', type='number', value=0.5,
                    min=0, max=1, step=0.01,
                    style={'width': '100%', 'marginBottom': '15px'})
            ]),

            html.Div([
                html.Label('Vaccine Effectiveness Lag (days)', style={'fontWeight': 'bold'}),
                html.Small('Number of days before vaccine starts to take effect. You can change this to alter your vaccine release time series as well.'),
                dcc.Input(id='vaccine-effectiveness-lag', type='number', value=14,
                    min=0, max=100, step=1,
                    style={'width': '100%', 'marginBottom': '15px'})
            ]),

            # Age-specific effectiveness
            html.Div([
                html.Label('Vaccine effectiveness (proportion)', style={'fontWeight': 'bold'}),
                html.Small('Age-specific effectiveness of vaccine against infection. 0 is not effective and 1 is completely effective',
                    style={'color': '#6c757d', 'display': 'block', 'marginBottom': '10px'}),

                html.Div([
                    html.Label('0-4 years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-eff-0-4', type='number', value=0.4,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('5-17 years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-eff-5-17', type='number', value=0.35,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('18-49 years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-eff-18-49', type='number', value=0.2,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('50-64 years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-eff-50-64', type='number', value=0.25,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('65+ years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-eff-65-plus', type='number', value=0.1,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '15px'})
                ])
            ]),

            # Age-specific adherence
            html.Div([
                html.Label('Vaccine adherence (proportion)', style={'fontWeight': 'bold'}),
                html.Small('Age-specific proportion of the population that will seek vaccination. 0 is no one and 1 is completely adherent',
                    style={'color': '#6c757d', 'display': 'block', 'marginBottom': '10px'}),

                html.Div([
                    html.Label('0-4 years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-adh-0-4', type='number', value=0.4,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('5-17 years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-adh-5-17', type='number', value=0.35,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('18-49 years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-adh-18-49', type='number', value=0.2,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('50-64 years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-adh-50-64', type='number', value=0.25,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '5px'})
                ]),
                html.Div([
                    html.Label('65+ years', style={'fontSize': '14px'}),
                    dcc.Input(id='vac-adh-65-plus', type='number', value=0.1,
                        step=0.01, min=0, max=1,
                        style={'width': '100%', 'marginBottom': '15px'})
                ])
            ]),

            # Vaccine stockpile section
            html.Label(['Vaccine Stockpile'], style={'fontWeight': 'bold'}),
            html.Small('Vaccine reserves available beginning on a specified day. Negative days are allowed to vaccinate people before epidemic begins on day 0.',
                style={'color': '#6c757d', 'display': 'block', 'marginBottom': '10px'}),

            html.Div([
                html.Label('Stockpile Day'),
                dcc.Input(id='vac-stockpile-day', type='number', min=-300, max=300,
                    placeholder="Specify stockpile day...",
                    style={'width': '100%', 'marginBottom': '10px'})
            ]),
            html.Div([
                html.Label('Stockpile Amount'),
                dcc.Input(id='vac-stockpile-amount', type='number', min=1,
                    placeholder="Specify stockpile amount...",
                    style={'width': '100%', 'marginBottom': '10px'})
            ]),
            html.Button('Add Vaccine Stockpile', id='add-vac-stockpile-btn',
                className='btn btn-secondary', style={'marginBottom': '15px'}),

            # Table showing added vaccine stockpiles
            html.Div(id='vac-stockpile-table')
        ])
    else:
        return html.Div([])


# Vaccine stockpile management callbacks
@callback(
    [Output('vaccine-stockpile', 'data'),
     Output('vac-stockpile-table', 'children'),],
    [Input('add-vac-stockpile-btn', 'n_clicks'),
     Input({'type': 'remove-vac-stockpile-btn', 'index': ALL}, 'n_clicks')],
    [State('vac-stockpile-day', 'value'),
     State('vac-stockpile-amount', 'value'),
     State('vaccine-stockpile', 'data'),],
    prevent_initial_call=True
)
def manage_vaccine_stockpile(add_clicks, remove_clicks, day, amount, current_data):
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None

    if 'add-vac-stockpile-btn' in triggered_id and day and amount:
        # Add new case
        new_case = {
            'id': len(current_data),
            'day': day,
            'amount': amount,
        }
        current_data.append(new_case)

    elif 'remove-vac-stockpile-btn' in triggered_id:
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
                    html.Td(f'{case["day"]}'),
                    html.Td(f'{case["amount"]}'),
                    html.Td(
                        html.Button('Remove',
                            id={'type': 'remove-vac-stockpile-btn', 'index': case['id']},
                            className='btn btn-sm btn-danger')
                    )
                ])
            )
        table = html.Table([
            html.Thead([
                html.Tr([
                    html.Th('Day'),
                    html.Th('Amount'),
                    html.Th('Action')
                ])
            ]),
            html.Tbody(table_rows)
        ], className='table table-striped')
    else:
        table = html.P('No stockpiles added yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})

    #logger.info(f'current_data = {current_data}')
    return current_data, table


# Add modals to layout
app.layout.children.extend([disease_params_modal, initial_cases_modal, npi_modal, antivirals_modal, vaccines_modal])


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('model-description-display', 'children'),
    Input('model-selector-dropdown', 'value')
)
def update_model_description(selected_model):
    """
    Updates the model description when user selects a model.
    """
    if not selected_model:
        return "Select a model to see its description."
    
    # Find the selected model's description
    for model in MODEL_OPTIONS:
        if model["value"] == selected_model:
            return html.Div([
                html.Span("ℹ️ ", style={'marginRight': '5px'}),
                html.Span(model["description"])
            ])
    
    return "Description not available."


@callback(
    [Output('model-state-status-message', 'children'),
     Output('selected-model-store', 'data'),
     Output('selected-state-store', 'data')],
    Input('apply-model-state-btn', 'n_clicks'),
    [State('model-selector-dropdown', 'value'),
     State('state-selector-dropdown', 'value')],
    prevent_initial_call=True
)
def apply_model_state_selection(n_clicks, selected_model, selected_state):
    """
    Handles the Apply button click.
    Saves the selected model and state to the stores.
    """
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Validate selections
    if not selected_model or not selected_state:
        error_msg = html.Div([
            html.Span("⚠️ ", style={'color': '#dc3545'}),
            "Please select both a model and a state."
        ], style={
            'padding': '10px',
            'backgroundColor': '#f8d7da',
            'color': '#721c24',
            'borderRadius': '5px',
            'fontSize': '13px'
        })
        return error_msg, dash.no_update, dash.no_update
    
    # Get display names
    model_name = next((m['label'] for m in MODEL_OPTIONS if m['value'] == selected_model), selected_model)
    state_name = next((s['label'] for s in STATE_OPTIONS if s['value'] == selected_state), selected_state)
    
    # Create success message
    success_msg = html.Div([
        html.Div([
            html.Span("✓ ", style={'color': '#28a745', 'fontWeight': 'bold'}),
            html.Span("Selection Applied!", style={'fontWeight': 'bold'})
        ]),
        html.Div([
            html.Span("Model: ", style={'fontWeight': 'bold'}),
            html.Span(model_name)
        ], style={'fontSize': '12px', 'marginTop': '5px'}),
        html.Div([
            html.Span("State: ", style={'fontWeight': 'bold'}),
            html.Span(state_name)
        ], style={'fontSize': '12px'})
    ], style={
        'padding': '10px',
        'backgroundColor': '#d4edda',
        'color': '#155724',
        'borderRadius': '5px',
        'border': '1px solid #c3e6cb'
    })
    
    logger.info(f"Model and State selection applied: Model={selected_model}, State={selected_state}")
    
    return success_msg, selected_model, selected_state


@callback(
    Output('location-assets-store', 'data'),
    Input('apply-model-state-btn', 'n_clicks'),
    State('state-selector-dropdown', 'value'),
    prevent_initial_call=True
)
def load_assets_for_selected_location(n_clicks, selected_state):
    if not n_clicks or not selected_state:
        return dash.no_update

    try:
        names, mapping, geojson = _load_location_assets(selected_state)
        logger.info(f"Loaded assets for {selected_state}: {len(names)} regions")
        return {"names": names, "mapping": mapping, "geojson": geojson}
    
    except Exception as e:
        logger.error(f"Failed to load assets for {selected_state}: {e}")
        return {"names": [], "mapping": {}, "geojson": None}


@callback(
    Output('initial-location', 'options'),
    Input('location-assets-store', 'data')
)
def update_initial_location_options(location_assets):
    if not location_assets:
        return []

    return [
        {"label": name, "value": name}
        for name in location_assets.get("names", [])
    ]


@callback(
    Output('npi-location', 'options'),
    Input('location-assets-store', 'data'),
)
def update_npi_location_options(location_assets):
    if not location_assets:
        return [{"label": "Statewide", "value": "Statewide"}]

    names = location_assets.get("names", [])
    return (
        [{"label": "Statewide", "value": "Statewide"}] +
        [{"label": n, "value": n} for n in names]
    )


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
     Output('latent-period', 'value'),
     Output('asymptomatic-period', 'value'),
     Output('symptomatic-period', 'value'),
     Output('cfr-0-4', 'value'),
     Output('cfr-5-24', 'value'),
     Output('cfr-25-49', 'value'),
     Output('cfr-50-64', 'value'),
     Output('cfr-65-plus', 'value'),
     Output('infectious-period', 'value'),
     Output('immune-period', 'value'),],
    Input('preset-scenario-dropdown', 'value'),
    State('model-selector-dropdown', 'value'),
    prevent_initial_call=True
)
def load_preset_scenario(preset_key, selected_value):
    scenario_prefix = selected_value.split('-')[0]

    if preset_key and preset_key in PRESET_SCENARIOS[scenario_prefix]:
        scenario = PRESET_SCENARIOS[scenario_prefix][preset_key]

        if scenario_prefix == 'seatird':
            return (
                scenario.get('disease_name', None),
                scenario.get('R0', None),
                scenario.get('tau', None),
                scenario.get('kappa', None),
                scenario.get('gamma', None),
                scenario.get('nu', [])[0],
                scenario.get('nu', [])[1],
                scenario.get('nu', [])[2],
                scenario.get('nu', [])[3],
                scenario.get('nu', [])[4],
                dash.no_update,
                dash.no_update
            )
        elif scenario_prefix == 'seirs':
            return (
                scenario.get('disease_name', None),
                scenario.get('R0', None),
                scenario.get('latent_period', None),
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                scenario.get('infectious_period', None),
                scenario.get('immune_period', None)
            )
    return [dash.no_update] * 12


# Load the correct disease parameters in the modal
@callback(
    [Output('disease-param-modal-display-asymptomatic', 'style'),
     Output('disease-param-modal-display-symptomatic', 'style'),
     Output('disease-param-modal-display-cfr', 'style'),
     Output('disease-param-modal-display-sigma', 'style'), 
     Output('disease-param-modal-display-infectious', 'style'), 
     Output('disease-param-modal-display-immune', 'style'),],
    Input('disease-params-modal', 'is_open'),
    State('model-selector-dropdown', 'value'),
    prevent_initial_call=True
)
def display_correct_disease_parameters(modal_is_open, selected_value):
    scenario_prefix = selected_value.split('-')[0]

    if scenario_prefix == 'seatird':
        return (
            {'display': 'block'},
            {'display': 'block'},
            {'display': 'block'},
            {'display': 'block'},
            {'display': 'none'},
            {'display': 'none'},
        )
    elif scenario_prefix == 'seirs':
        return (
            {'display': 'none'},
            {'display': 'none'},
            {'display': 'none'},
            {'display': 'none'},
            {'display': 'block'},
            {'display': 'block'},
        )
    
    return [dash.no_update] * 6


# Initial cases management callbacks
@callback(
    [Output('initial-cases-data', 'data'),
     Output('initial-cases-table', 'children'),
     Output('play-pause-btn', 'disabled', allow_duplicate=True)],
    [Input('add-initial-case-btn', 'n_clicks'),
     Input({'type': 'remove-case-btn', 'index': ALL}, 'n_clicks')],
    [State('initial-location', 'value'),
     State('initial-cases-count', 'value'),
     State('initial-age-group', 'value'),
     State('initial-cases-data', 'data'),
     State('location-assets-store', 'data'),
     State('disease-parameters', 'data')],
    prevent_initial_call=True
)
def manage_initial_cases(add_clicks, remove_clicks, location, cases_count, age_group, current_data, location_assets, disease_params):
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None

    mapping = (location_assets or {}).get("mapping", {})

    if 'add-initial-case-btn' in triggered_id and location and cases_count:
        # Add new case
        fips_id = mapping.get(location, '0')
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
    
    play_disabled = not (bool(disease_params) and bool(current_data) and len(current_data) > 0)
    
    return current_data, table, play_disabled


# Disease parameters save callback
@callback(
    [Output('disease-parameters', 'data'),
     Output('displayed-parameters-content', 'children', allow_duplicate=True),
     Output('play-pause-btn', 'disabled', allow_duplicate=True)],
    Input('disease-params-save', 'n_clicks'),
    [State('scenario-name', 'value'),
     State('reproduction-number', 'value'),
     State('latent-period', 'value'),
     State('asymptomatic-period', 'value'),
     State('symptomatic-period', 'value'),
     State('cfr-0-4', 'value'),
     State('cfr-5-24', 'value'),
     State('cfr-25-49', 'value'),
     State('cfr-50-64', 'value'),
     State('cfr-65-plus', 'value'),
     State('sigma-0-4', 'value'),
     State('sigma-5-24', 'value'),
     State('sigma-25-49', 'value'),
     State('sigma-50-64', 'value'),
     State('sigma-65-plus', 'value'),
     State('infectious-period', 'value'),
     State('immune-period', 'value'),
     State('initial-cases-data', 'data'),
     State('displayed-tab', 'data'),
     State('selected-model-store', 'data'),],
    prevent_initial_call=True
)
def save_disease_parameters(n_clicks, scenario_name, r0, tau, kappa, gamma, 
                          cfr_0_4, cfr_5_24, cfr_25_49, cfr_50_64, cfr_65_plus,
                          sigma_0_4, sigma_5_24, sigma_25_49, sigma_50_64, sigma_65_plus,
                          infectious_period, immune_period,
                          initial_cases, displayed_tab, selected_model):
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
            'nu': [cfr_0_4 or 0, cfr_5_24 or 0, cfr_25_49 or 0, cfr_50_64 or 0, cfr_65_plus or 0],
            'sigma': [sigma_0_4 or 1, sigma_5_24 or 1, sigma_25_49 or 1, sigma_50_64 or 1, sigma_65_plus or 1],
            'infectious_period': infectious_period or 7,
            'immune_period': immune_period or 0,
            'model_type': selected_model,
        }
        
        logger.info('saved disease parameters = ')
        logger.info(disease_params)
        #TODO fix this to only display relevant parameters for disease model selected
        # Update displayed parameters
        if displayed_tab == 'scenario':
            content = create_scenario_display(disease_params, initial_cases)
        else:
            content = html.P('No interventions set yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})
        
        # Enable play button ONLY if we have BOTH disease parameters AND initial cases
        play_disabled = not (bool(disease_params) and bool(initial_cases) and len(initial_cases) > 0)
        
        
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
     State('vaccine-data', 'data'),
     State('vaccine-stockpile', 'data')],
    prevent_initial_call=True
)
def switch_displayed_tab(scenario_clicks, interventions_clicks, disease_params, initial_cases, 
                        npi_data, antiviral_data, vaccine_data, vaccine_stockpile):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'scenario-tab-btn'
    
    if triggered_id == 'interventions-tab-btn':
        content = create_interventions_display(npi_data, antiviral_data, vaccine_data, vaccine_stockpile)
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

        if disease_params['model_type'].startswith('seatird-'):
            content.extend([
                html.H6('Disease Parameters', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P(f"Scenario: {disease_params.get('scenario_name', 'Custom')}"),
                html.P(f"Reproduction Number: {disease_params.get('R0', 0)}"),
                html.P(f"Latent Period: {disease_params.get('tau', 0)} days"),
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
        if disease_params['model_type'].startswith('seirs-'):
            content.extend([
                html.H6('Disease Parameters', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                html.P(f"Scenario: {disease_params.get('scenario_name', 'Custom')}"),
                html.P(f"Reproduction Number: {disease_params.get('R0', 0)}"),
                html.P(f"Latent Period: {disease_params.get('tau', 0)} days"),
                html.P(f"Infectious Period: {disease_params.get('infectious_period', 0)} days"),
                html.P(f"Immune Period: {disease_params.get('immune_period', 0)} days"),
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
# NPI callback
@callback(
    [Output('npi-data', 'data'),
     Output('npi-table', 'children')],
    [Input('add-npi-btn', 'n_clicks'),
     Input({'type': 'remove-npi-btn', 'index': ALL}, 'n_clicks')],
    [State('npi-name', 'value'),
     State('npi-start', 'value'),
     State('npi-duration', 'value'),
     State('npi-eff-0-4', 'value'),
     State('npi-eff-5-24', 'value'),
     State('npi-eff-25-49', 'value'),
     State('npi-eff-50-64', 'value'),
     State('npi-eff-65-plus', 'value'),
     State('npi-location', 'value'),
     State('npi-data', 'data')],
    prevent_initial_call=True
)
def manage_npis(add_clicks, remove_clicks,
                name, start, duration,
                eff_0_4, eff_5_24, eff_25_49, eff_50_64, eff_65_plus,
                location, current_npi_data):

    current_npi_data = list(current_npi_data or [])
    trig = ctx.triggered_id  # structured; no regex needed

    if trig == 'add-npi-btn':
        # Basic validation
        if not name:
            # no change, but still render table
            return current_npi_data, _render_npi_table(current_npi_data)

        if start is None:
            start = 5
        if duration is None:
            duration = 30

        # Preserve 0.0 values: use "is None" checks instead of "or"
        effectiveness = [
            0.4 if eff_0_4 is None else eff_0_4,
            0.35 if eff_5_24 is None else eff_5_24,
            0.2 if eff_25_49 is None else eff_25_49,
            0.25 if eff_50_64 is None else eff_50_64,
            0.1 if eff_65_plus is None else eff_65_plus,
        ]

        # multi=True should be list; normalize defensively
        if not location:
            location = ['Statewide']
        elif isinstance(location, str):
            location = [location]

        current_npi_data.append({
            'name': name,
            'start': int(start),
            'duration': int(duration),
            'effectiveness': effectiveness,
            'location': location
        })

        return current_npi_data, _render_npi_table(current_npi_data)

    # ----- Remove -----
    if isinstance(trig, dict) and trig.get("type") == "remove-npi-btn":
        idx = trig.get("index")
        if isinstance(idx, int) and 0 <= idx < len(current_npi_data):
            current_npi_data.pop(idx)

        return current_npi_data, _render_npi_table(current_npi_data)

    # Fallback: nothing changed
    return current_npi_data, _render_npi_table(current_npi_data)


def _render_npi_table(npi_list):
    if not npi_list:
        return dash.html.P('No NPIs added yet.', style={'color': '#6c757d', 'fontStyle': 'italic'})

    rows = []
    for i, npi in enumerate(npi_list):
        rows.append(
            dash.html.Tr([
                dash.html.Td(npi.get('name', '')),
                dash.html.Td(f"Day {npi.get('start', '')} for {npi.get('duration', '')} days"),
                dash.html.Td(", ".join(npi.get('location', []))),
                dash.html.Td(
                    dash.html.Button(
                        'Remove',
                        id={'type': 'remove-npi-btn', 'index': i},
                        className='btn btn-sm btn-danger'
                    )
                )
            ])
        )

    return dash.html.Table([
        dash.html.Thead(dash.html.Tr([
            dash.html.Th('NPI'),
            dash.html.Th('Timing'),
            dash.html.Th('Location'),
            dash.html.Th('Action')
        ])),
        dash.html.Tbody(rows)
    ], className='table table-striped')


@callback(
    Output('displayed-parameters-content', 'children', allow_duplicate=True),
    [Input('displayed-tab', 'data'),
     Input('disease-parameters', 'data'),
     Input('initial-cases-data', 'data'),
     Input('npi-data', 'data'),
     Input('antiviral-data', 'data'),
     Input('vaccine-data', 'data'),
     Input('vaccine-stockpile', 'data')],
    prevent_initial_call=True
)
def refresh_displayed_parameters(displayed_tab, disease_params, initial_cases, npi_data, antiviral_data, vaccine_data, vaccine_stockpile):
    """
    Keeps the Displayed Parameters panel in sync.
    This replaces the "refresh" behavior that used to live inside save_npi.
    """
    if displayed_tab == 'interventions':
        return create_interventions_display(npi_data or [], antiviral_data or {}, vaccine_data or {}, vaccine_stockpile or [])
    return create_scenario_display(disease_params or {}, initial_cases or [])

# Antiviral callback
@callback(
    [Output('antiviral-effectiveness', 'value'),
     Output('antiviral-wastage', 'value'),
     Output('antiviral-stockpile-day', 'value'),
     Output('antiviral-stockpile-amount', 'value')],
    Input('antivirals-modal', 'is_open'),
    State('antiviral-data', 'data'),
    prevent_initial_call=True
)
def prefill_antivirals_modal(is_open, antiviral_data):
    if not is_open:
        return [dash.no_update] * 4
    if antiviral_data:
        return (
            antiviral_data.get('effectiveness', 0.15),
            antiviral_data.get('wastage_factor', 60),
            antiviral_data.get('stockpile_day', 50),
            antiviral_data.get('stockpile_amount', 10000),
        )
    return (0.15, 60, 50, 10000)

@callback(
    [Output('antiviral-data', 'data'),
     Output('antivirals-enabled', 'data'),
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
     State('vaccine-data', 'data'),
     State('vaccine-stockpile', 'data')],
    prevent_initial_call=True
)
def save_antivirals(n_clicks, effectiveness, wastage, stockpile_day, stockpile_amount,
                    displayed_tab, disease_params, initial_cases, npi_data, vaccine_data, vaccine_stockpile):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update

    antiviral_data = {
        'effectiveness': 0.15 if effectiveness is None else effectiveness,
        'wastage_factor': 60 if wastage is None else wastage,
        'stockpile_day': 50 if stockpile_day is None else stockpile_day,
        'stockpile_amount': 10000 if stockpile_amount is None else stockpile_amount
    }

    if displayed_tab == 'interventions':
        content = create_interventions_display(npi_data or [], antiviral_data, vaccine_data or {}, vaccine_stockpile or [])
    else:
        content = create_scenario_display(disease_params or {}, initial_cases or [])

    return antiviral_data, True, content


@callback(
    [Output('vaccine-data', 'data'),
     Output('vaccines-enabled', 'data'),
     Output('displayed-parameters-content', 'children', allow_duplicate=True)],
    Input('vaccines-save', 'n_clicks'),
    [State('vaccine-model-dropdown', 'value'),
     State('vaccine-age-risk-priority-groups', 'value'),
     State('vaccine-capacity', 'value'),
     State('vaccine-effectiveness-lag', 'value'),
     State('vac-eff-0-4', 'value'),
     State('vac-eff-5-17', 'value'),
     State('vac-eff-18-49', 'value'),
     State('vac-eff-50-64', 'value'),
     State('vac-eff-65-plus', 'value'),
     State('vac-adh-0-4', 'value'),
     State('vac-adh-5-17', 'value'),
     State('vac-adh-18-49', 'value'),
     State('vac-adh-50-64', 'value'),
     State('vac-adh-65-plus', 'value'),
     State('vaccine-stockpile', 'data'),
     State('displayed-tab', 'data'),
     State('npi-data', 'data'),
     State('antiviral-data', 'data'),
     State('disease-parameters', 'data'),
     State('initial-cases-data', 'data'),],
    prevent_initial_call=True
)
def save_vaccines(n_clicks, vaccine_model,
                  priority_groups, capacity, effectiveness_lag,
                  vac_eff_0, vac_eff_1, vac_eff_2, vac_eff_3, vac_eff_4,
                  vac_adh_0, vac_adh_1, vac_adh_2, vac_adh_3, vac_adh_4,
                  vaccine_stockpile, displayed_tab, npi_data, antiviral_data,
                  disease_params, initial_cases):
    if not n_clicks:
        return [dash.no_update] * 4

    arpgs = ['vac-arpg-0-4', 'vac-arpg-5-17', 'vac-arpg-18-49', 'vac-arpg-50-64', 'vac-arpg-65-plus']

    vaccine_data = {
        'vaccine_model': vaccine_model,
        'priority_groups': [1 if value in priority_groups else 0 for value in arpgs],
        'capacity': capacity,
        'effectiveness_lag': effectiveness_lag,
        'effectiveness': [vac_eff_0, vac_eff_1, vac_eff_2, vac_eff_3, vac_eff_4],
        'adherence': [vac_adh_0, vac_adh_1, vac_adh_2, vac_adh_3, vac_adh_4],
    }

    logger.info(f'vaccine_data = {vaccine_data}')
    logger.info(f'vaccine_stockpile = {vaccine_stockpile}')

    if displayed_tab == 'interventions':
        content = create_interventions_display(npi_data or [], antiviral_data or {}, vaccine_data, vaccine_stockpile)
    else:
        content = create_scenario_display(disease_params or {}, initial_cases or [])

    return vaccine_data, True, content


def create_interventions_display(npi_data, antiviral_data, vaccine_data, vaccine_stockpile):
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
    
    ## Vaccines section
    if vaccine_data:
        model_label = 'Stockpile Age Risk' if vaccine_data['vaccine_model'] == 'stockpile-age-risk' else 'Undefined'
        content.extend([html.H6('Vaccines', style={'fontWeight': 'bold', 'marginBottom': '10px'})])
        content.append(html.Div([
            html.P(f"Vaccine Model: {model_label}"),
            html.P(f"Priority Groups: {vaccine_data['priority_groups']}"),
            html.P(f"Capacity: {vaccine_data['capacity']} (proportion)"),
            html.P(f"Effectiveness Lag: {vaccine_data['effectiveness_lag']} days"),
            html.P(f"Effectiveness:"),
            html.Ul([
                    html.Li(f"0-4: {vaccine_data['effectiveness'][0]:.2f}"),
                    html.Li(f"5-17: {vaccine_data['effectiveness'][1]:.2f}"),
                    html.Li(f"18-49: {vaccine_data['effectiveness'][2]:.2f}"),
                    html.Li(f"50-64: {vaccine_data['effectiveness'][3]:.2f}"),
                    html.Li(f"65+: {vaccine_data['effectiveness'][4]:.2f}")
            ], style={'marginLeft': '20px'}),
            html.P(f"Adherence:"),
            html.Ul([
                    html.Li(f"0-4: {vaccine_data['adherence'][0]:.2f}"),
                    html.Li(f"5-17: {vaccine_data['adherence'][1]:.2f}"),
                    html.Li(f"18-49: {vaccine_data['adherence'][2]:.2f}"),
                    html.Li(f"50-64: {vaccine_data['adherence'][3]:.2f}"),
                    html.Li(f"65+: {vaccine_data['adherence'][4]:.2f}")
            ], style={'marginLeft': '20px'}),
            html.P(f"Stockpile:"),
            html.Ul(children=[html.Li(f'day={i["day"]} , amt={i["amount"]}') for i in vaccine_stockpile], style={'marginLeft': '20px'})
        ], style={'marginBottom': '15px', 'padding': '10px', 'border': '1px solid #dee2e6', 'borderRadius': '4px'}))
    
    return html.Div(content)


# Reset callback - connects to Django backend
@callback(
    Output('simulation-state', 'data', allow_duplicate=True),
    Input('reset-btn', 'n_clicks'),
    State('simulation-state', 'data'),
    prevent_initial_call=True
)
def reset_simulation(n_clicks, sim_state):
    if n_clicks:
        logger.info("Resetting simulation...")

        if sim_state.get('isRunning'):
            try:
                task_id = sim_state.get('taskId')
                if task_id:
                    requests.get(f'{API_BASE_URL}/api/delete/{task_id}')
            except:
                pass

            new_state = {**sim_state, 'isRunning': False}

        else:
            new_state = {**sim_state}

        response = requests.get(f'{API_BASE_URL}/api/reset')
        logger.info(f"Reset response status: {response.status_code}")
        if response.status_code == 200:
            logger.info("Simulation reset successfully on backend.")

        return new_state

    return dash.no_update


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
     State('vaccine-data', 'data'),
     State('vaccine-stockpile', 'data'),
     State('antivirals-enabled', 'data'),
     State('vaccines-enabled', 'data'),
     State('selected-model-store', 'data'),
     State('selected-state-store', 'data')],
    prevent_initial_call=True
)
def toggle_simulation(n_clicks, sim_state, disease_params, initial_cases, npi_data, antiviral_data, vaccine_data,
                     vaccine_stockpile, antivirals_enabled, vaccines_enabled, selected_model, selected_state):
    if n_clicks and disease_params:
        is_running = sim_state.get('isRunning', False)
        
        if not is_running:
            # Start simulation - call Django backend exactly like React
            try:
                logger.info("Starting new simulation...")
                logger.info(f"Using Model: {selected_model}, State: {selected_state}")  # NEW: Log selection
                
                # Format parameters for Django API exactly like React
                payload = {
                    'disease_name': disease_params.get('scenario_name', 'Custom'),
                    'model_type': selected_model or 'seirs-deterministic',
                    'state': selected_state or 'Alabama',
                    'R0': disease_params.get('R0', 1.2),
                    'beta_scale': disease_params.get('beta_scale', 10.0),
                    'tau': disease_params.get('tau', 1.2),
                    'kappa': disease_params.get('kappa', 1.9),
                    'gamma': disease_params.get('gamma', 4.1),
                    'chi': disease_params.get('chi', 1.0),
                    'rho': disease_params.get('rho', 0.39),
                    'nu': ','.join(map(str, disease_params.get('nu', [0,0,0,0,0]))),
                    'sigma': ','.join(map(str, disease_params.get('sigma', [1,1,1,1,1]))),
                    'infectious_period': disease_params.get('infectious_period', 14),
                    'immune_period': disease_params.get('immune_period', 0),
                }

                # Add initial cases - use provided cases or default to Harris County
                initial_infected = []
                if initial_cases:
                    for case in initial_cases:
                        initial_infected.append({
                            'county': case['fips_id'],
                            'infected': case['cases'],
                            'age_group': case['age_group_id']
                        })

                payload['initial_infected'] = json.dumps(initial_infected)

                # Add default empty values for required fields
                # baseline defaults
                payload.update({
                    'npis': json.dumps([]),
                    'antiviral_model': json.dumps({}),
                    'vaccine_model': json.dumps({}),
                })

                # Add NPIs
                if npi_data:
                    npis = []
                    for npi in npi_data:
                        npis.append({
                            'type': npi['name'],
                            'day': npi['start'],
                            'duration': npi['duration'],
                            'effectiveness': npi['effectiveness'],
                            'location': npi['location']
                        })
                    payload['npis'] = json.dumps(npis)

                # Antivirals only if enabled
                #if antivirals_enabled and antiviral_data:
                #    payload.update({
                #        'antiviral_effectiveness': antiviral_data['effectiveness'],
                #        'antiviral_stockpile': antiviral_data['stockpile_amount'],
                #        'antiviral_wastage_factor': antiviral_data['wastage_factor'] / 365.0
                #    })

                # Add vaccines
                if vaccines_enabled and vaccine_data:
                    payload.update({
                        'vaccine_model': vaccine_data['vaccine_model'],
                        'vaccine_priority_groups': json.dumps(vaccine_data['priority_groups']),
                        'vaccine_capacity': vaccine_data['capacity'],
                        'vaccine_effectiveness_lag': vaccine_data['effectiveness_lag'],
                        'vaccine_effectiveness': json.dumps(vaccine_data['effectiveness']),
                        'vaccine_adherence': json.dumps(vaccine_data['adherence']),
                    })
                
                    payload.update({
                        'vaccine_stockpile': json.dumps(vaccine_stockpile)
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
        current_day = len(event_data) # Start from day 0
        
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

                            # Infectious should be all infectious compartments
                            A = compartment_summary.get('A', 0) or 0
                            I = compartment_summary.get('I', 0) or 0
                            T = compartment_summary.get('T', 0) or 0
                            infected = round(A + I + T, 2)

                            attempt_d = compartment_summary.get('D', None)
                            if attempt_d is None:
                                deceased = round(compartment_summary.get('R', 0), 2)
                            else:
                                deceased = round(attempt_d, 2)
                            
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
     Input('view-toggle', 'value'),
     Input('location-assets-store', 'data')],
    State('selected-model-store', 'data')
)
def update_map(event_data, timeline_value, view_type, location_assets, selected_model):
    """Update map with county-level choropleth visualization"""
    
    geojson = location_assets.get("geojson") if location_assets else None
    
    # Show empty map with state boundaries if no simulation data yet
    if geojson and (not event_data or len(event_data) == 0):
        logger.info("Displaying empty map with state boundaries")
        return _create_empty_state_map(geojson)
    
    # DEBUG LOGGING
    logger.info(
        f"map debug → "
        f"event_days={len(event_data) if event_data else 0}, "
        f"timeline={timeline_value}, "
        f"geojson_loaded={bool(geojson)}"
    )

    return _create_jurisdiction_choropleth(event_data, timeline_value, view_type, geojson, selected_model)


@callback(
    Output('line-chart', 'figure'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value')],
    State('selected-model-store', 'data')
)
def update_chart(event_data, timeline_value, selected_model):
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

    # Decide which series to show
    model = (selected_model or "").lower()
    if model.startswith("seir") or model.startswith("seirs"):
        # SEIR
        series = [
            ("Susceptible", susceptible),
            ("Exposed", exposed),
            ("Infectious", infected),
            ("Recovered", recovered),
        ]
    else:
        # SEATIRD
        series = [
            ("Susceptible", susceptible),
            ("Exposed", exposed),
            ("Asymptomatic Infectious", asymptomatic),
            ("Treatable Infectious", treatable),
            ("Symptomatic Infectious", infected),
            ("Recovered", recovered),
            ("Deceased", deceased),
        ]

    # Add traces for SEATIRD compartments
    COLOR_MAP = {
        "Susceptible": "blue",
        "Exposed": "orange",
        "Asymptomatic Infectious": "gold",
        "Treatable Infectious": "purple",
        "Symptomatic Infectious": "red",
        "Infectious": "red",
        "Recovered": "green",
        "Deceased": "black",
    }
    fig = go.Figure()
    for name, y in series:
        fig.add_trace(
            go.Scatter(
                x=days,
                y=y,
                name=name,
                line=dict(color=COLOR_MAP.get(name))
            )
        )
    
    # Add vertical line for current day
    if timeline_value is not None and timeline_value < len(days):
        fig.add_vline(x=timeline_value, line_dash="dash", line_color="gray", annotation_text=f"Day {timeline_value}")
    
    fig.update_layout(
        title=dict(
            #text="Epidemic Curve", # remove title to make space for legend
            y=0.96,
            yanchor='top',
            pad=dict(t=5)
        ),
        xaxis_title="Day",
        yaxis_title="Population Count",
        height=300,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=70),
        hovermode='x unified'
    )

    return fig

@callback(
    [Output('spread-table', 'children'),
    Output('county-table-sort', 'data')],
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value'),
     Input('location-assets-store', 'data'),
     Input('county-search', 'value'),
     Input('sort-location', 'n_clicks'),
     Input('sort-infected', 'n_clicks'),
     Input('sort-deceased', 'n_clicks')],
    [State('county-table-sort', 'data'),
     State('selected-model-store', 'data')]
)
def update_table(event_data, timeline_value, view_type, location_assets, search_text,
                 location_clicks, infected_clicks, deceased_clicks, sort_state, selected_model):
    # --- sort state update based on which header was clicked
    sort_state = sort_state or {'col': 'infected', 'dir': 'desc'}

    model = (selected_model or "").lower()
    right_col_label = "Recovered" if model.startswith("seir") or model.startswith("seirs") else "Deceased"

    if not event_data or timeline_value is None or timeline_value >= len(event_data):
        return html.P('No data available', style={'color': '#6c757d', 'fontStyle': 'italic'}), sort_state
    
    current_data = event_data[timeline_value]
    counties_data = current_data.get('counties', [])
    if not counties_data:
        return html.P('No county data available', style={'color': '#6c757d', 'fontStyle': 'italic'}), sort_state

    trig = ctx.triggered_id
    if trig == 'sort-location':
        if sort_state.get('col') == 'name':
            sort_state['dir'] = 'asc' if sort_state['dir'] == 'desc' else 'desc'
        else:
            sort_state = {'col': 'name', 'dir': 'desc'}
    elif trig == 'sort-infected':
        if sort_state.get('col') == 'infected':
            sort_state['dir'] = 'asc' if sort_state.get('dir') == 'desc' else 'desc'
        else:
            sort_state = {'col': 'infected', 'dir': 'desc'}
    elif trig == 'sort-deceased':
        if sort_state.get('col') == 'deceased':
            sort_state['dir'] = 'asc' if sort_state.get('dir') == 'desc' else 'desc'
        else:
            sort_state = {'col': 'deceased', 'dir': 'desc'}


    location_assets = location_assets or {}
    mapping = location_assets.get("mapping", {})  # name -> geoid (string)

    # Invert mapping once: geoid -> name
    id_to_name = {str(geoid): name for name, geoid in mapping.items() if str(name).lower() != "all"}

    # Create table data
    table_data = []
    for county in counties_data:
        geoid = str(county.get('fips', '')).strip()
        if not geoid:
            continue

        # Ensure FIPS format matches GeoJSON geoid (5-digit county format)
        if(len(geoid)==4): # Leading 0s of states are getting lost
            geoid = geoid.zfill(5)

        county_name = (id_to_name.get(geoid) or geoid)  # final fallback: show id

        # keep numeric for sorting + searching
        infected_num = float(county.get('infectedPercent', 0)) if view_type == 'percent' else float(
            county.get('infected', 0))
        deceased_num = float(county.get('deceasedPercent', 0)) if view_type == 'percent' else float(
            county.get('deceased', 0))

        if view_type == 'percent':
            infected_disp = f"{infected_num:.1f}%"
            deceased_disp = f"{deceased_num:.1f}%"
        else:
            infected_disp = f"{math.floor(infected_num):,}"
            deceased_disp = f"{math.floor(deceased_num):,}"

        table_data.append({
            "name": county_name,
            "infected_num": infected_num,
            "deceased_num": deceased_num,
            "infected_disp": infected_disp,
            "deceased_disp": deceased_disp,
        })

        # --- search (works for numbers because we search stringified values too)
        if search_text:
            q = search_text.strip().lower()

            def matches(r):
                hay = f"{r['name']} {r['infected_num']} {r['deceased_num']} {r['infected_disp']} {r['deceased_disp']}".lower()
                return q in hay

            table_data = [r for r in table_data if matches(r)]

    if not table_data:
        return html.P('No county data available', style={'color': '#6c757d', 'fontStyle': 'italic'}), sort_state

    # --- sort
    key = {
        'name': 'name',
        'infected': 'infected_num',
        'deceased': 'deceased_num'
    }[sort_state['col']]
    reverse = (sort_state['dir'] == 'desc')
    table_data.sort(key=lambda r: r[key], reverse=reverse)

    # --- header with clickable sort buttons (minimal styling)
    arrow_loc = '▲' if sort_state['col'] == 'name' and sort_state['dir'] == 'asc' else (
        '▼' if sort_state['col'] == 'name' else '')
    arrow_inf = '▼' if sort_state['col'] == 'infected' and sort_state['dir'] == 'desc' else (
        '▲' if sort_state['col'] == 'infected' else '')
    arrow_dec = '▼' if sort_state['col'] == 'deceased' and sort_state['dir'] == 'desc' else (
        '▲' if sort_state['col'] == 'deceased' else '')

    header = html.Thead(html.Tr([
        html.Th(html.Button(f'Location {arrow_loc}', id='sort-location', n_clicks=0,
                            style={'border': 'none', 'background': 'transparent', 'padding': 0, 'fontWeight': 'bold',
                                   'minWidth': '90px'})),
        html.Th(html.Button(f'Infectious {arrow_inf}', id='sort-infected', n_clicks=0,
                            style={'border': 'none', 'background': 'transparent', 'padding': 0, 'fontWeight': 'bold',
                                   'minWidth': '90px'})),
        html.Th(html.Button(f'{right_col_label} {arrow_dec}', id='sort-deceased', n_clicks=0,
                            style={'border': 'none', 'background': 'transparent', 'padding': 0, 'fontWeight': 'bold',
                                   'minWidth': '90px'})),
    ]))

    body = html.Tbody([
        html.Tr([html.Td(r["name"]), html.Td(r["infected_disp"]), html.Td(r["deceased_disp"])])
        for r in table_data
    ])

    table = dbc.Table(
        [header, body],
        bordered=True,
        hover=True,
        striped=True,
        responsive=False,
        className="w-100",
        style={'maxHeight': '800px', 'overflowY': 'auto', 'display': 'block', 'tableLayout': 'fixed'}
    )

    return table, sort_state

# Expose server for deployment
server = app.server

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8051)


