import glob
import json
import logging
import math
import os

import dash
from dash import dcc, html, Input, Output, State, callback, ctx, ALL, register_page
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import requests

from constants import (
    MODEL_OPTIONS,
    PRESET_SCENARIOS,
    AGE_GROUPS,
    AGE_GROUP_MAPPING,
    VACCINE_MODELS,
    API_BASE_URL,
)

register_page(__name__, path='/', title='epiENGAGE Home')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dirs with spatial data (names and polygons)
ASSETS_DIR = 'assets'
name_dir = os.path.join(ASSETS_DIR, 'fips_to_names')
geo_dir = os.path.join(ASSETS_DIR, 'map_boundaries')


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
    mapping_prefixes = {_get_prefix(f) for f in os.listdir(mapping_dir) if f.endswith('.json')}

    boundary_prefixes = {
        _get_prefix(f) for f in os.listdir(boundaries_dir) if f.endswith('.geojson')
    }

    prefixes = (
        mapping_prefixes & boundary_prefixes
        if require_both
        else mapping_prefixes | boundary_prefixes
    )

    options = []
    for value in sorted(prefixes):
        label = value.replace('-', ' ')  # US_JURISDICTION_LABELS.get(value,
        options.append({'label': label, 'value': value})

    return options


STATE_OPTIONS = _build_jurisdiction_options(name_dir, geo_dir, require_both=True)


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
    name_path = _first_match(os.path.join(name_dir, f'{location_value}_*.json'))
    if not name_path:
        raise FileNotFoundError(
            f"Missing name mapping for '{location_value}'. "
            f'Expected {name_dir}/{location_value}_*.json'
        )

    with open(name_path, 'r') as f:
        mapping = json.load(f)

    names = [k for k in mapping.keys() if k.lower() != 'all']

    # ---- geometry (required)
    geo_path = _first_match(os.path.join(geo_dir, f'{location_value}_*.geojson')) or _first_match(
        os.path.join(geo_dir, f'{location_value}_*.json')
    )
    if not geo_path:
        raise FileNotFoundError(
            f"Missing geometry for '{location_value}'. "
            f'Expected {geo_dir}/{location_value}_*.geojson (or .json)'
        )

    with open(geo_path, 'r') as f:
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
        paper_bgcolor='white',
        plot_bgcolor='white',
        title='Map - No Data Available',
    )
    return fig


def _add_county_polygon(lons, lats, color, county_name, infections=None):
    """Create a county to add to the state map"""
    if not infections:
        text = f'{county_name} - No data yet - click PLAY to start simulation'
    else:
        text = f'{county_name}<br>Infectious: {infections["infected"]:,} ({infections["infected_pct"]:.1f}%)<br>Recovered: {infections["deceased"]:,} ({infections["deceased_pct"]:.1f}%)'
    return go.Scatter(
        x=lons,
        y=lats,
        fill='toself',
        fillcolor=color,
        line=dict(color='darkgray', width=0.5),
        mode='lines',
        name=county_name,
        showlegend=False,
        text=text,
        hoverinfo='text',
    )


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

                    fig.add_trace(_add_county_polygon(lons, lats, '#FFEDA0', county_name))
        else:
            # Single Polygon
            for ring in coordinates:
                lons = [coord[0] for coord in ring]
                lats = [coord[1] for coord in ring]

                fig.add_trace(_add_county_polygon(lons, lats, '#FFEDA0', county_name))

    fig.update_layout(
        title='Map - No Data Available (Select disease parameters and click PLAY)',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(
            showgrid=False, showticklabels=False, zeroline=False, scaleanchor='x', scaleratio=1
        ),
        hovermode='closest',
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

    logger.info(
        f'Creating county map for day {current_data.get("day", 0)} with {len(counties_data)} counties'
    )

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
            full_fips = f'48{fips}'
        elif len(fips) == 4:  # Leading 0s of states are getting lost
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
            'deceasedPercent': county.get('deceasedPercent', 0),
        }

        # Debug logging for first few counties
        if len(county_values) <= 3:
            pass
            logger.info(
                f'County {full_fips}: Infectious={county.get("infected", 0)}, percent={county.get("infectedPercent", 0)}'
            )

    logger.info(f'Mapped {len(county_values)} counties to FIPS codes')

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

        infections = {
            'infected': infected,
            'infected_pct': infected_pct,
            'deceased': deceased,
            'deceased_pct': deceased_pct,
        }

        # Extract coordinates for the county polygon
        coordinates = feature['geometry']['coordinates']

        # Handle MultiPolygon vs Polygon
        if feature['geometry']['type'] == 'MultiPolygon':
            for polygon in coordinates:
                for ring in polygon:
                    lons = [coord[0] for coord in ring]
                    lats = [coord[1] for coord in ring]

                    model = (selected_model or '').lower()
                    if model.startswith('seir') or model.startswith('seirs'):
                        fig.add_trace(
                            _add_county_polygon(lons, lats, color, county_name, infections)
                        )
                    else:
                        fig.add_trace(
                            _add_county_polygon(lons, lats, color, county_name, infections)
                        )
        else:
            # Single Polygon
            for ring in coordinates:
                lons = [coord[0] for coord in ring]
                lats = [coord[1] for coord in ring]

                fig.add_trace(_add_county_polygon(lons, lats, color, county_name, infections))

    # Configure layout to match React version exactly
    fig.update_layout(
        title=f'Day {current_data.get("day", 0)} ({"Percentage" if view_type == "percent" else "Count"} View)',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(
            showgrid=False, showticklabels=False, zeroline=False, scaleanchor='x', scaleratio=1
        ),
        hovermode='closest',
    )

    fig.update_xaxes(autorange=True)
    fig.update_yaxes(autorange=True)

    logger.info('Successfully created county map with individual polygons')
    return fig


# ============================================================================
# MODALS
# ============================================================================


# Input helper
def create_modal_footer(prefix: str, note: bool):
    """Create a standard Save/Close modal footer. prefix is the modal name, e.g. 'npi'."""
    note_content = []
    if note:
        note_content = [
            html.Span('ℹ️ ', className='model-setup__desc-icon'),
            html.Span('Add at least 1 initial case to save.'),
        ]
    return dbc.ModalFooter(
        html.Div(
            [
                html.Div(
                    [
                        dbc.Button(
                            'SAVE',
                            id=f'{prefix}-save',
                            n_clicks=0,
                            color='success',
                            class_name='me-2 modal-form__footer-button',
                        ),
                        dbc.Button(
                            'CLOSE',
                            id=f'{prefix}-close',
                            n_clicks=0,
                            class_name='modal-form__footer-button',
                            color='danger',
                        ),
                    ],
                    className='d-flex justify-content-center mb-2',
                ),
                html.Div(
                    note_content,
                    id=f'{prefix}-footer-note',
                    className='text-center modal-form__footer-info',
                ),
            ],
            className='w-100',
        ),
        class_name='bg-light',
    )


def create_labeled_input(label: str, input_id: str, **kwargs):
    """Create a plain Label + full-width Input wrapped in a Div."""
    return html.Div(
        className='modal-form__field dbc',
        children=[
            dbc.Label(label),
            dbc.Input(id=input_id, className='mb-3', **kwargs),
        ],
    )


def create_bold_label_subtitle_number_input(label: str, subtitle: str, inputs: list):
    """
    Each element in inputs: {input_label, input_id, input_value, input_step, input_min}
    Set input_label to None for a single unlabelled input.
    """

    def make_input(spec):
        field = dbc.Input(
            id=spec['input_id'],
            type='number',
            value=spec['input_value'],
            step=spec['input_step'],
            min=spec['input_min'],
            className='mb-2 dbc',
        )
        if spec['input_label'] is not None:
            return html.Div(
                [dbc.Label(spec['input_label'], class_name='modal-form__label small'), field],
            )
        return field

    return html.Div(
        className='modal-form__field',
        children=[
            dbc.Label(label, class_name='modal-form__label fw-bold'),
            html.Small(subtitle, className='modal-form__subtitle'),
        ]
        + [make_input(spec) for spec in inputs],
    )


# Disease Parameters Modal Component
disease_params_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle('Disease Parameters'), class_name='modal-form__header'),
        dbc.ModalBody(
            id='disease-params-modal-body',
            class_name='bg-light',
        ),
        create_modal_footer('disease-params', False),
    ],
    id='disease-params-modal',
    is_open=False,
    size='lg',
)


# Initial Cases Modal Component
initial_cases_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle('Initial Cases'), class_name='modal-form__header'),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        dbc.Label('Location'),
                        html.Div(
                            dcc.Dropdown(
                                id='initial-location',
                                options=[],
                                placeholder='Search for a location...',
                                className='dbc',
                            ),
                            id='initial-location-wrapper',
                        ),
                        html.Div(
                            'Please select a location.',
                            id='initial-location-feedback',
                            className='invalid-feedback',
                            style={'display': 'none'},
                        ),
                    ],
                    className='mb-3 dbc',
                ),
                html.Div(
                    [
                        dbc.Label('Number of Cases'),
                        html.Div(
                            dbc.Input(id='initial-cases-count', type='number', value=100, min=1),
                            id='initial-cases-count-wrapper',
                        ),
                        html.Div(
                            'Please enter at least 1 case.',
                            id='initial-cases-count-feedback',
                            className='invalid-feedback',
                            style={'display': 'none'},
                        ),
                    ],
                    className='mb-3',
                ),
                html.Div(
                    [
                        dbc.Label('Age Group'),
                        html.Div(
                            dcc.Dropdown(
                                id='initial-age-group',
                                options=AGE_GROUPS,
                                value='18-49 years',
                            ),
                            id='initial-age-group-wrapper',
                        ),
                        html.Div(
                            'Please select an age group.',
                            id='initial-age-group-feedback',
                            className='invalid-feedback',
                            style={'display': 'none'},
                        ),
                    ],
                    className='mb-4 dbc',
                ),
                html.Button(
                    'Add Initial Case',
                    id='add-initial-case-btn',
                    className='btn btn-primary mb-3',
                ),
                # Table showing added initial cases
                html.Div(id='initial-cases-table'),
            ],
            class_name='bg-light',
        ),
        create_modal_footer('initial-cases', True),
    ],
    id='initial-cases-modal',
    is_open=False,
    centered=True,
    size='lg',
)


# NPI (Non-Pharmaceutical Interventions) Modal Component
npi_modal = dbc.Modal(
    [
        dbc.ModalHeader(
            dbc.ModalTitle('Non-Pharmaceutical Interventions'), class_name='modal-form__header'
        ),
        dbc.ModalBody(
            [
                create_labeled_input('NPI Name', 'npi-name', type='text', value='School Closures'),
                create_labeled_input(
                    'NPI start (simulation day)',
                    'npi-start',
                    type='number',
                    value=5,
                    min=0,
                    max=1000,
                    step=1,
                ),
                create_labeled_input(
                    'NPI duration (days)',
                    'npi-duration',
                    type='number',
                    value=30,
                    min=1,
                    max=1000,
                    step=1,
                ),
                # Age-specific effectiveness section
                create_bold_label_subtitle_number_input(
                    label='NPI effectiveness (proportion)',
                    subtitle='Age-specific effectiveness values',
                    inputs=[
                        {
                            'input_label': '0-4 years',
                            'input_id': 'npi-eff-0-4',
                            'input_value': 0.4,
                            'input_step': 0.01,
                            'input_min': 0,
                        },
                        {
                            'input_label': '5-17 years',
                            'input_id': 'npi-eff-5-24',
                            'input_value': 0.35,
                            'input_step': 0.01,
                            'input_min': 0,
                        },
                        {
                            'input_label': '18-49 years',
                            'input_id': 'npi-eff-25-49',
                            'input_value': 0.2,
                            'input_step': 0.01,
                            'input_min': 0,
                        },
                        {
                            'input_label': '50-64 years',
                            'input_id': 'npi-eff-50-64',
                            'input_value': 0.25,
                            'input_step': 0.01,
                            'input_min': 0,
                        },
                        {
                            'input_label': '65+ years',
                            'input_id': 'npi-eff-65-plus',
                            'input_value': 0.1,
                            'input_step': 0.01,
                            'input_min': 0,
                        },
                    ],
                ),
                # Location selection
                html.Div(
                    [
                        dbc.Label('Location'),
                        dcc.Dropdown(
                            id='npi-location',
                            options=[],
                            value=['Statewide'],
                            multi=True,
                            className='mb-3',
                        ),
                    ],
                    className='modal-form__field dbc',
                ),
                html.Button(
                    'Add NPI',
                    id='add-npi-btn',
                    className='btn btn-primary mb-3',
                ),
                # Table showing added NPIs
                html.Div(id='npi-table'),
            ],
            class_name='bg-light',
        ),
        create_modal_footer('npi', False),
    ],
    id='npi-modal',
    is_open=False,
    size='lg',
)

# Antivirals Modal Component
antivirals_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle('Antivirals'), class_name='modal-form__header'),
        dbc.ModalBody(
            [
                create_labeled_input(
                    'Antiviral Effectiveness',
                    'antiviral-effectiveness',
                    type='number',
                    value=0.15,
                    min=0,
                    max=1,
                    step=0.01,
                ),
                create_labeled_input(
                    'Antiviral Wastage Factor (days)',
                    'antiviral-wastage',
                    type='number',
                    value=60,
                    min=0,
                    max=1000,
                    step=1,
                ),
                html.H6('Stockpile Management', className='fw-bold mb-2'),
                create_labeled_input(
                    'New Stockpile Day',
                    'antiviral-stockpile-day',
                    type='number',
                    value=50,
                    min=1,
                    max=1000,
                    step=1,
                ),
                create_labeled_input(
                    'New Stockpile Amount',
                    'antiviral-stockpile-amount',
                    type='number',
                    value=10000,
                    min=0,
                    step=1,
                ),
            ],
            class_name='bg-light',
        ),
        create_modal_footer('antivirals', False),
    ],
    id='antivirals-modal',
    is_open=False,
)


# Vaccines Modal Component
vaccines_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle('Vaccines'), class_name='modal-form__header'),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        dbc.Label('Vaccine Model', class_name='fw-bold'),
                        dcc.Dropdown(
                            options=[
                                {'label': model, 'value': key}
                                for key, model in VACCINE_MODELS.items()
                            ],
                            placeholder='Select a vaccine model...',
                            clearable=True,
                            className='mb-3',
                            id='vaccine-model-dropdown',
                        ),
                    ],
                    className='modal-form__field dbc',
                ),
                html.Hr(),
                html.Div(
                    id='vaccine-parameter-body',
                    style={'display': 'none'},
                    children=[
                        # Vaccine priority groups
                        html.Div(
                            [
                                dbc.Label('Vaccine Priority Groups', class_name='fw-bold'),
                                html.Small(
                                    'Select age specific priority groups for vaccine distribution',
                                    className='modal-form__subtitle',
                                ),
                                dbc.Checklist(
                                    id='vaccine-age-risk-priority-groups',
                                    options=[
                                        {'label': '0-4 years', 'value': 'vac-arpg-0-4'},
                                        {'label': '5-17 years', 'value': 'vac-arpg-5-17'},
                                        {'label': '18-49 years', 'value': 'vac-arpg-18-49'},
                                        {'label': '50-64 years', 'value': 'vac-arpg-50-64'},
                                        {'label': '65+ years', 'value': 'vac-arpg-65-plus'},
                                    ],
                                    value=['vac-arpg-18-49'],
                                    input_class_name='me-2',
                                    label_class_name='modal-form__checklist-label',
                                ),
                            ],
                            className='modal-form__field mb-3',
                        ),
                        html.Div(
                            [
                                dbc.Label('Vaccine Half Life (days)', class_name='fw-bold'),
                                html.Small(
                                    'Number of days required to clear half the vaccine from the body'
                                ),
                                dbc.Input(
                                    id='vaccine-half-life',
                                    type='number',
                                    value=60,
                                    min=0,
                                    max=1000,
                                    step=1,
                                    className='mb-3',
                                ),
                            ],
                            style={'display': 'none'},
                        ),  ### This is currently hidden ###
                        html.Div(
                            [
                                dbc.Label('Vaccine Capacity (proportion)', class_name='fw-bold'),
                                html.Small(
                                    'Proportion of population the jurisdiction has the capacity to vaccinate per day, from 0 to 1'
                                ),
                                dbc.Input(
                                    id='vaccine-capacity',
                                    type='number',
                                    value=0.5,
                                    min=0,
                                    max=1,
                                    step=0.01,
                                    className='mb-3',
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                dbc.Label('Vaccine Effectiveness Lag (days)', class_name='fw-bold'),
                                html.Small(
                                    'Number of days before vaccine starts to take effect. You can change this to alter your vaccine release time series as well.'
                                ),
                                dbc.Input(
                                    id='vaccine-effectiveness-lag',
                                    type='number',
                                    value=14,
                                    min=0,
                                    max=100,
                                    step=1,
                                    className='mb-3',
                                ),
                            ]
                        ),
                        # Age-specific effectiveness
                        create_bold_label_subtitle_number_input(
                            label='Vaccine effectiveness (proportion)',
                            subtitle='Age-specific effectiveness of vaccine against infection. 0 is not effective and 1 is completely effective',
                            inputs=[
                                {
                                    'input_label': '0-4 years',
                                    'input_id': 'vac-eff-0-4',
                                    'input_value': 0.4,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                                {
                                    'input_label': '5-17 years',
                                    'input_id': 'vac-eff-5-17',
                                    'input_value': 0.35,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                                {
                                    'input_label': '18-49 years',
                                    'input_id': 'vac-eff-18-49',
                                    'input_value': 0.2,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                                {
                                    'input_label': '50-64 years',
                                    'input_id': 'vac-eff-50-64',
                                    'input_value': 0.25,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                                {
                                    'input_label': '65+ years',
                                    'input_id': 'vac-eff-65-plus',
                                    'input_value': 0.1,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                            ],
                        ),
                        # Age-specific adherence
                        create_bold_label_subtitle_number_input(
                            label='Vaccine adherence (proportion)',
                            subtitle='Age-specific proportion of the population that will seek vaccination. 0 is no one and 1 is completely adherent',
                            inputs=[
                                {
                                    'input_label': '0-4 years',
                                    'input_id': 'vac-adh-0-4',
                                    'input_value': 0.4,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                                {
                                    'input_label': '5-17 years',
                                    'input_id': 'vac-adh-5-17',
                                    'input_value': 0.35,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                                {
                                    'input_label': '18-49 years',
                                    'input_id': 'vac-adh-18-49',
                                    'input_value': 0.2,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                                {
                                    'input_label': '50-64 years',
                                    'input_id': 'vac-adh-50-64',
                                    'input_value': 0.25,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                                {
                                    'input_label': '65+ years',
                                    'input_id': 'vac-adh-65-plus',
                                    'input_value': 0.1,
                                    'input_step': 0.01,
                                    'input_min': 0,
                                },
                            ],
                        ),
                        # Vaccine stockpile section
                        dbc.Label('Vaccine Stockpile', class_name='fw-bold'),
                        html.Small(
                            'Vaccine reserves available beginning on a specified day. Negative days are allowed to vaccinate people before epidemic begins on day 0.',
                            className='modal-form__subtitle',
                        ),
                        create_labeled_input(
                            'Stockpile Day',
                            'vac-stockpile-day',
                            type='number',
                            min=-300,
                            max=300,
                            placeholder='Specify stockpile day...',
                        ),
                        create_labeled_input(
                            'Stockpile Amount',
                            'vac-stockpile-amount',
                            type='number',
                            min=1,
                            placeholder='Specify stockpile amount...',
                        ),
                        html.Button(
                            'Add Vaccine Stockpile',
                            id='add-vac-stockpile-btn',
                            className='btn btn-primary mb-3',
                        ),
                        html.Div(id='vac-stockpile-table'),
                    ],
                ),
            ],
            class_name='bg-light',
        ),
        create_modal_footer('vaccines', False),
    ],
    id='vaccines-modal',
    is_open=False,
)


# ============================================================================
# FUNCTIONS TO CREATE ELEMENTS FOR MAIN CONTENT AREA
# ============================================================================
def create_model_state_selection_panel():
    """
    Creates the Model and State selection dropdowns.
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.Span(
                            [
                                html.I(className='bi bi-1-circle-fill me-2'),
                                html.Span('Start Simulation Setup'),
                            ]
                        ),
                        html.Span(
                            html.I(className='bi bi-caret-up-fill', id='sim-setup-caret'),
                            className='model-setup__header-btn',
                        ),
                    ],
                    id='sim-setup-header',
                    n_clicks=0,
                    className='model-setup__header',
                ),
                className='model-setup__header-bg model-setup__header-height',
            ),
            dbc.Collapse(
                [
                    dbc.CardBody(
                        [
                            # Model Selection Dropdown
                            html.Div(
                                [
                                    dbc.Label('Disease Model', class_name='fw-bold'),
                                    dcc.Dropdown(
                                        id='model-selector-dropdown',
                                        options=[
                                            {'label': m['label'], 'value': m['value']}
                                            for m in MODEL_OPTIONS
                                        ],
                                        value='seirs-deterministic',
                                        clearable=True,
                                        placeholder='Select a disease model...',
                                        className='mb-2',
                                    ),
                                    # Model description display
                                    html.Div(
                                        id='model-description-display',
                                        className='model-setup__desc',
                                    ),
                                ]
                            ),
                            # State Selection Dropdown
                            html.Div(
                                [
                                    dbc.Label('State', class_name='fw-bold'),
                                    dcc.Dropdown(
                                        id='state-selector-dropdown',
                                        options=[
                                            {'label': s['label'], 'value': s['value']}
                                            for s in STATE_OPTIONS
                                        ],
                                        value='Alabama',
                                        clearable=True,
                                        searchable=True,
                                        placeholder='Select a state...',
                                        className='mb-3',
                                    ),
                                ]
                            ),
                            # Apply Button
                            dbc.Button(
                                'APPLY SELECTION',
                                id='apply-model-state-btn',
                                n_clicks=0,
                                class_name='model-setup__apply-btn btn-navy',
                            ),
                            # Status message area
                            html.Div(id='model-state-status-message'),
                        ],
                        class_name='model-setup__body',
                    )
                ],
                id='sim-setup-collapse',
                is_open=True,
            ),
        ],
        class_name='mb-3',
    )


def create_set_scenario_panel():
    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.Span(
                            [
                                html.I(className='bi bi-2-circle-fill me-2'),
                                html.Span('Set Scenario'),
                            ]
                        ),
                        html.Span(
                            html.I(className='bi bi-caret-down-fill', id='sim-scenario-caret'),
                            className='model-setup__header-btn',
                        ),
                    ],
                    id='sim-scenario-header',
                    n_clicks=0,
                    className='model-setup__header',
                ),
                className='model-setup__header-bg model-setup__header-height',
            ),
            dbc.Collapse(
                dbc.CardBody(
                    html.Div(
                        [
                            dbc.Button(
                                'Set Disease Parameters',
                                id='disease-params-btn',
                                outline=True,
                                color='dark',
                                n_clicks=0,
                                class_name='model-setup__set-content-btn',
                            ),
                            dbc.Button(
                                'Set Initial Cases',
                                id='initial-cases-btn',
                                outline=True,
                                color='dark',
                                n_clicks=0,
                                class_name='model-setup__set-content-btn',
                            ),
                        ],
                        className='d-grid gap-2',
                    ),
                    class_name='model-setup__body',
                ),
                id='sim-scenario-collapse',
                is_open=False,
            ),
        ],
        class_name='mb-3',
    )


def create_set_interventions_panel():
    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.Span(
                            [
                                html.I(className='bi bi-3-circle-fill me-2'),
                                html.Span(
                                    [
                                        'Interventions ',
                                        html.Span('(optional)', className='fw-light'),
                                    ]
                                ),
                            ]
                        ),
                        html.Span(
                            html.I(className='bi bi-caret-down-fill', id='sim-interventions-caret'),
                            className='model-setup__header-btn',
                        ),
                    ],
                    id='sim-interventions-header',
                    n_clicks=0,
                    className='model-setup__header',
                ),
                className='model-setup__header-bg model-setup__header-height',
            ),
            dbc.Collapse(
                dbc.CardBody(
                    html.Div(
                        [
                            dbc.Button(
                                'Select Non-Pharmaceutical',
                                id='npi-btn',
                                outline=True,
                                color='dark',
                                n_clicks=0,
                                class_name='model-setup__set-content-btn',
                            ),
                            dbc.Button(
                                'Select Antivirals',
                                id='antivirals-btn',
                                outline=True,
                                color='dark',
                                n_clicks=0,
                                style={'display': 'none'},
                            ),  ### Remove this style to show Antiviral button ###
                            dbc.Button(
                                'Select Vaccines',
                                id='vaccines-btn',
                                outline=True,
                                color='dark',
                                n_clicks=0,
                                class_name='model-setup__set-content-btn',
                            ),
                        ],
                        className='d-grid gap-2',
                    ),
                    class_name='model-setup__body',
                ),
                id='sim-interventions-collapse',
                is_open=False,
            ),
        ],
        class_name='mb-3',
    )


def create_displayed_parameters_panel():
    return dbc.Tabs(
        [
            dbc.Tab(
                html.Div(
                    id='scenario-content',
                    children=[
                        html.P('No scenario set yet.', className='param-display__empty-state')
                    ],
                    className='param-display__content',
                ),
                label='Scenario',
                tab_id='tab-scenario',
                tab_class_name='param-display__tab-item',
                label_class_name='param-display__tab-left',
            ),
            dbc.Tab(
                html.Div(
                    id='interventions-content',
                    children=[
                        html.P('No interventions set yet.', className='param-display__empty-state')
                    ],
                    className='param-display__content',
                ),
                label='Interventions',
                tab_id='tab-interventions',
                tab_class_name='param-display__tab-item',
                label_class_name='param-display__tab-right',
            ),
        ],
        id='param-tabs',
        active_tab='tab-scenario',
        class_name='param-display__tabs model-setup__header-height',
        # model-setup__header-bg
    )


# Home page layout
def create_home_layout():
    return html.Div(
        [
            dcc.Location(id='url', refresh=True),
            # Main content row with fixed height
            html.Div(
                [
                    # Left Panel - Settings
                    html.Div(
                        [
                            html.Div(
                                [
                                    create_model_state_selection_panel(),
                                    create_set_scenario_panel(),
                                    create_set_interventions_panel(),
                                    create_displayed_parameters_panel(),
                                ],
                                className='sim-layout__left',
                            )
                        ],
                        className='sim-layout__col--left',
                    ),
                    # Middle Panel - Map and Chart
                    html.Div(
                        [
                            # View toggle (count/percent)
                            html.Div(
                                [
                                    html.H6('Show values as:', className='mb-2'),
                                    dbc.RadioItems(
                                        id='view-toggle',
                                        options=[
                                            {'label': ' Percentage', 'value': 'percent'},
                                            {'label': ' Count', 'value': 'count'},
                                        ],
                                        value='count',
                                        inline=True,
                                        label_class_name='view-toggle__label',
                                        class_name='mb-3 ps-2',
                                    ),
                                ],
                                className='sim-layout__middle-header',
                            ),
                            # Map and Chart container
                            html.Div(
                                [
                                    # Map
                                    dcc.Graph(
                                        id='spread-map',
                                        className='sim-layout__map',
                                        config={'displayModeBar': False},
                                    ),
                                    # Line Chart
                                    dcc.Graph(
                                        id='line-chart',
                                        className='sim-layout__chart',
                                        config={'displayModeBar': False},
                                    ),
                                ],
                                className='sim-layout__viz',
                            ),
                        ],
                        className='sim-layout__col--middle',
                    ),
                    # Right Panel - Table
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6('County Data', className='mb-2'),
                                    dbc.Input(
                                        id='county-search',
                                        type='text',
                                        placeholder='Search (county or number)…',
                                        debounce=True,
                                        class_name='mb-2',
                                    ),
                                    dcc.Store(
                                        id='county-table-sort',
                                        data={'col': 'infected', 'dir': 'desc'},
                                    ),
                                    html.Div(
                                        id='spread-table',
                                        className='sim-layout__table',
                                    ),
                                ],
                                className='sim-layout__right',
                            )
                        ],
                        className='sim-layout__col--right',
                    ),
                ],
                className='sim-layout__row',
            ),
            # Footer - OUTSIDE the row, always visible at bottom
            html.Div(
                [
                    html.Div(
                        [
                            # Reset Button
                            dbc.Button(
                                'Reset',
                                id='reset-btn',
                                color='danger',
                                class_name='sim-footer__reset-btn',
                            ),
                            # Play/Pause Button
                            dbc.Button(
                                'Play',
                                id='play-pause-btn',
                                color='success',
                                disabled=True,
                                class_name='sim-footer__play-btn',
                            ),
                            # Timeline Slider
                            html.Div(
                                [
                                    dcc.Slider(
                                        id='timeline-slider',
                                        min=0,
                                        step=1,
                                        value=0,
                                        marks={i: str(i) for i in range(0, 201, 5)},
                                        tooltip={'placement': 'bottom', 'always_visible': True},
                                        disabled=True,
                                    )
                                ],
                                className='sim-footer__slider',
                            ),
                        ],
                        className='sim-footer__controls',
                    )
                ],
                className='sim-footer',
            ),
            disease_params_modal,
            initial_cases_modal,
            npi_modal,
            antivirals_modal,
            vaccines_modal,
        ],
    )


def create_interventions_display(npi_data, antiviral_data, vaccine_data, vaccine_stockpile):
    """Create interventions tab display content"""
    if not npi_data and not antiviral_data and not vaccine_data:
        return html.P('No interventions set yet.', className='param-display__empty-state')

    content = []

    # NPIs section
    if npi_data:
        content.extend(
            [
                html.H6('Non-Pharmaceutical Interventions', className='fw-light mb-2'),
            ]
        )
        for npi in npi_data:
            content.append(
                html.Div(
                    [
                        html.P([html.Span('Name: ', className='fw-bold'), npi['name']]),
                        html.P(
                            [
                                html.Span('Start Day: ', className='fw-bold'),
                                f'{npi["start"]}, ',
                                html.Span('Duration: ', className='fw-bold'),
                                f'{npi["duration"]} days',
                            ]
                        ),
                        html.P(
                            [
                                html.Span('Location: ', className='fw-bold'),
                                ', '.join(npi['location']),
                            ]
                        ),
                        html.P(html.Span('Age-specific effectiveness:', className='fw-bold')),
                        html.Ul(
                            [
                                html.Li(f'0-4: {npi["effectiveness"][0]:.2f}'),
                                html.Li(f'5-24: {npi["effectiveness"][1]:.2f}'),
                                html.Li(f'25-49: {npi["effectiveness"][2]:.2f}'),
                                html.Li(f'50-64: {npi["effectiveness"][3]:.2f}'),
                                html.Li(f'65+: {npi["effectiveness"][4]:.2f}'),
                            ],
                            className='ms-3',
                        ),
                    ],
                    className='param-display__card',
                )
            )

    # Antivirals section
    if antiviral_data:
        content.extend(
            [
                html.H6('Antivirals', className='fw-light mb-2'),
                html.P(
                    [
                        html.Span('Effectiveness: ', className='fw-bold'),
                        f'{antiviral_data["effectiveness"]:.2f}',
                    ]
                ),
                html.P(
                    [
                        html.Span('Wastage Factor: ', className='fw-bold'),
                        f'{antiviral_data["wastage_factor"]} days',
                    ]
                ),
                html.P(
                    [
                        html.Span('Stockpile: ', className='fw-bold'),
                        f'{antiviral_data["stockpile_amount"]} on day {antiviral_data["stockpile_day"]}',
                    ]
                ),
            ]
        )

    ## Vaccines section
    if vaccine_data:
        model_label = (
            'Stockpile Age Risk'
            if vaccine_data['vaccine_model'] == 'stockpile-age-risk'
            else 'Undefined'
        )
        content.extend([html.H6('Vaccines', className='fw-light mb-2')])
        content.append(
            html.Div(
                [
                    html.P([html.Span('Vaccine Model: ', className='fw-bold'), model_label]),
                    html.P(
                        [
                            html.Span('Priority Groups: ', className='fw-bold'),
                            f'{vaccine_data["priority_groups"]}',
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Capacity: ', className='fw-bold'),
                            f'{vaccine_data["capacity"]} (proportion)',
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Effectiveness Lag: ', className='fw-bold'),
                            f'{vaccine_data["effectiveness_lag"]} days',
                        ]
                    ),
                    html.P(html.Span('Effectiveness:', className='fw-bold')),
                    html.Ul(
                        [
                            html.Li(f'0-4: {vaccine_data["effectiveness"][0]:.2f}'),
                            html.Li(f'5-17: {vaccine_data["effectiveness"][1]:.2f}'),
                            html.Li(f'18-49: {vaccine_data["effectiveness"][2]:.2f}'),
                            html.Li(f'50-64: {vaccine_data["effectiveness"][3]:.2f}'),
                            html.Li(f'65+: {vaccine_data["effectiveness"][4]:.2f}'),
                        ],
                        className='ms-3',
                    ),
                    html.P(html.Span('Adherence:', className='fw-bold')),
                    html.Ul(
                        [
                            html.Li(f'0-4: {vaccine_data["adherence"][0]:.2f}'),
                            html.Li(f'5-17: {vaccine_data["adherence"][1]:.2f}'),
                            html.Li(f'18-49: {vaccine_data["adherence"][2]:.2f}'),
                            html.Li(f'50-64: {vaccine_data["adherence"][3]:.2f}'),
                            html.Li(f'65+: {vaccine_data["adherence"][4]:.2f}'),
                        ],
                        className='ms-3',
                    ),
                    html.P(html.Span('Stockpile:', className='fw-bold')),
                    html.Ul(
                        children=[
                            html.Li(f'day={i["day"]} , amt={i["amount"]}')
                            for i in vaccine_stockpile
                        ],
                        className='ms-3',
                    ),
                ],
                className='param-display__card',
            )
        )

    return html.Div(content)


def create_scenario_display(disease_params, initial_cases):
    """Create scenario tab display content"""
    if not disease_params and not initial_cases:
        return html.P('No scenario set yet.', className='param-display__empty-state')

    content = []

    title_class = 'text-muted'

    # Disease parameters section
    if disease_params:
        if disease_params['model_type'].startswith('seatird-'):
            content.extend(
                [
                    html.H6('Disease Parameters', className=title_class),
                    html.Hr(),
                    html.P(
                        [
                            html.Span('Scenario: ', className='fw-bold'),
                            disease_params.get('scenario_name', 'Custom'),
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Reproduction Number: ', className='fw-bold'),
                            disease_params.get('R0', 0),
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Latent Period: ', className='fw-bold'),
                            f'{disease_params.get("tau", 0)} days',
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Asymptomatic Period: ', className='fw-bold'),
                            f'{disease_params.get("kappa", 0)} days',
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Symptomatic Period: ', className='fw-bold'),
                            f'{disease_params.get("gamma", 0)} days',
                        ]
                    ),
                    html.P(html.Span('Case Fatality Rate:', className='fw-bold')),
                    html.Ul(
                        [
                            html.Li(f'0-4: {disease_params.get("nu", [0, 0, 0, 0, 0])[0]:.9f}'),
                            html.Li(f'5-24: {disease_params.get("nu", [0, 0, 0, 0, 0])[1]:.9f}'),
                            html.Li(f'25-49: {disease_params.get("nu", [0, 0, 0, 0, 0])[2]:.9f}'),
                            html.Li(f'50-64: {disease_params.get("nu", [0, 0, 0, 0, 0])[3]:.9f}'),
                            html.Li(f'65+: {disease_params.get("nu", [0, 0, 0, 0, 0])[4]:.9f}'),
                        ],
                        className='ms-3 mb-3',
                    ),
                ]
            )
        if disease_params['model_type'].startswith('seirs-'):
            content.extend(
                [
                    html.H6('Disease Parameters', className=title_class),
                    html.Hr(),
                    html.P(
                        [
                            html.Span('Scenario: ', className='fw-bold'),
                            disease_params.get('scenario_name', 'Custom'),
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Reproduction Number: ', className='fw-bold'),
                            disease_params.get('R0', 0),
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Latent Period: ', className='fw-bold'),
                            f'{disease_params.get("tau", 0)} days',
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Infectious Period: ', className='fw-bold'),
                            f'{disease_params.get("infectious_period", 0)} days',
                        ]
                    ),
                    html.P(
                        [
                            html.Span('Immune Period: ', className='fw-bold'),
                            f'{disease_params.get("immune_period", 0)} days',
                        ]
                    ),
                ]
            )

    # Initial cases section
    if initial_cases:
        content.extend(
            [
                html.H6('Initial Cases', className='fw-bold mb-2'),
                html.Ul(
                    [
                        html.Li(f'{case["cases"]} aged {case["age_group"]} in {case["location"]}')
                        for case in initial_cases
                    ],
                    className='ms-3',
                ),
            ]
        )

    if not content:
        return html.P('No scenario set yet.', className='param-display__empty-state')

    return html.Div(content, className='mt-0')


def _render_npi_table(npi_list):
    if not npi_list:
        return dash.html.P('No NPIs added yet.', className='param-display__empty-state')

    rows = []
    for i, npi in enumerate(npi_list):
        rows.append(
            dash.html.Tr(
                [
                    dash.html.Td(npi.get('name', '')),
                    dash.html.Td(f'Day {npi.get("start", "")} for {npi.get("duration", "")} days'),
                    dash.html.Td(', '.join(npi.get('location', []))),
                    dash.html.Td(
                        dash.html.Button(
                            'Remove',
                            id={'type': 'remove-npi-btn', 'index': i},
                            className='btn btn-sm btn-danger',
                        )
                    ),
                ]
            )
        )

    return dash.html.Table(
        [
            dash.html.Thead(
                dash.html.Tr(
                    [
                        dash.html.Th('NPI'),
                        dash.html.Th('Timing'),
                        dash.html.Th('Location'),
                        dash.html.Th('Action'),
                    ]
                )
            ),
            dash.html.Tbody(rows),
        ],
        className='table table-striped',
    )


# ============================================================================
# LAYOUT
# ============================================================================


def layout(**kwargs):
    layout = create_home_layout()
    return layout


# ============================================================================
# CALLBACKS
# ============================================================================


@callback(
    Output('sim-setup-collapse', 'is_open'),
    Output('sim-setup-caret', 'className'),
    [Input('sim-setup-header', 'n_clicks')],
    [State('sim-setup-collapse', 'is_open')],
)
def toggle_collapse(n, is_open):
    new_open = (not is_open) if n else is_open
    caret = 'bi bi-caret-up-fill' if new_open else 'bi bi-caret-down-fill'
    return new_open, caret


@callback(
    Output('disease-params-modal-body', 'children'),
    Input('model-selector-dropdown', 'value'),
    Input('disease-preset-store', 'data'),
    Input('disease-params-modal', 'is_open'),
    prevent_initial_call=True,
)
def update_disease_param_modal_body(selected_value, preset, is_open):
    if not is_open:
        return dash.no_update
    if selected_value is None:
        return dbc.ModalBody(
            ['Select a valid disease model to set parameters.'], class_name='bg-light'
        )

    scenario_prefix = selected_value.split('-')[0]
    preset = preset or {}

    modal_elems = [
        html.Div(
            [
                dbc.Label('Load from Catalog', class_name='fw-bold'),
                dcc.Dropdown(
                    id={'type': 'dp-dropdown', 'param': 'preset'},
                    options=[
                        {'label': scenario['name'], 'value': key}
                        for key, scenario in PRESET_SCENARIOS[scenario_prefix].items()
                    ],
                    placeholder='Select a preset scenario...',
                    className='mb-3',
                ),
            ],
            className='dbc',
        ),
        html.Hr(),
        html.Div(
            [
                dbc.Label('Scenario Name', class_name='fw-bold'),
                dbc.Input(
                    id={'type': 'dp-input', 'param': 'scenario-name'},
                    type='text',
                    value=preset.get('disease_name', ''),
                    className='mb-3',
                ),
            ]
        ),
        create_bold_label_subtitle_number_input(
            label='Reproduction Number (R₀)',
            subtitle=' - Average number of secondary infections in a susceptible population',
            inputs=[
                {
                    'input_label': None,
                    'input_id': {'type': 'dp-input', 'param': 'reproduction-number'},
                    'input_value': preset.get('R0', 1.2),
                    'input_step': 0.1,
                    'input_min': 0,
                }
            ],
        ),
        create_bold_label_subtitle_number_input(
            label='Latent period (days)',
            subtitle=' - Average number of days from infection to infectiousness',
            inputs=[
                {
                    'input_label': None,
                    'input_id': {'type': 'dp-input', 'param': 'latent-period'},
                    'input_value': preset.get('tau', preset.get('latent_period', 1.2)),
                    'input_step': 0.1,
                    'input_min': 0,
                }
            ],
        ),
    ]

    if scenario_prefix == 'seatird':
        modal_elems.extend(
            [
                create_bold_label_subtitle_number_input(
                    label='Asymptomatic period (days)',
                    subtitle=' - Average number of days spent infectious, but not yet symptomatic',
                    inputs=[
                        {
                            'input_label': None,
                            'input_id': {'type': 'dp-input', 'param': 'asymptomatic-period'},
                            'input_value': preset.get('kappa', 1.9),
                            'input_step': 0.1,
                            'input_min': 0,
                        }
                    ],
                ),
                create_bold_label_subtitle_number_input(
                    label='Symptomatic period (days)',
                    subtitle=' - Average number of days spent symptomatic and infectious',
                    inputs=[
                        {
                            'input_label': None,
                            'input_id': {'type': 'dp-input', 'param': 'symptomatic-period'},
                            'input_value': preset.get('gamma', 4.1),
                            'input_step': 0.1,
                            'input_min': 0,
                        }
                    ],
                ),
                create_bold_label_subtitle_number_input(
                    label='Mortality rate (1/days)',
                    subtitle=' - Inverse average number of days spent asymptomatic/treatable/infectious to deceased',
                    inputs=[
                        {
                            'input_label': label,
                            'input_id': {'type': 'dp-input', 'param': param},
                            'input_value': preset.get(
                                'nu',
                                [0.000022319, 0.000040975, 0.000083729, 0.000061809, 0.000008978],
                            )[i],
                            'input_step': 0.000000001,
                            'input_min': 0,
                        }
                        for i, (label, param) in enumerate(
                            [
                                ('0-4 years', 'cfr-0-4'),
                                ('5-17 years', 'cfr-5-24'),
                                ('18-49 years', 'cfr-25-49'),
                                ('50-64 years', 'cfr-50-64'),
                                ('65+ years', 'cfr-65-plus'),
                            ]
                        )
                    ],
                ),
                create_bold_label_subtitle_number_input(
                    label='Relative susceptibility (ratio)',
                    subtitle=' - How susceptible each age group is relative to a reference group (e.g. 0-4yro)',
                    inputs=[
                        {
                            'input_label': label,
                            'input_id': {'type': 'dp-input', 'param': param},
                            'input_value': preset.get('sigma', [1.0, 1.0, 1.0, 1.0, 1.0])[i],
                            'input_step': 0.000000001,
                            'input_min': 0,
                        }
                        for i, (label, param) in enumerate(
                            [
                                ('0-4 years', 'sigma-0-4'),
                                ('5-17 years', 'sigma-5-24'),
                                ('18-49 years', 'sigma-25-49'),
                                ('50-64 years', 'sigma-50-64'),
                                ('65+ years', 'sigma-65-plus'),
                            ]
                        )
                    ],
                ),
            ]
        )
    elif scenario_prefix == 'seirs':
        modal_elems.extend(
            [
                create_bold_label_subtitle_number_input(
                    label='Infectious period (days)',
                    subtitle=' - Average number of days spent infectious',
                    inputs=[
                        {
                            'input_label': None,
                            'input_id': {'type': 'dp-input', 'param': 'infectious-period'},
                            'input_value': preset.get('infectious_period', 1.9),
                            'input_step': 0.1,
                            'input_min': 0,
                        }
                    ],
                ),
                create_bold_label_subtitle_number_input(
                    label='Immune period (days)',
                    subtitle=' - Average number of days before returning to susceptible (set to 0 to make this an SEIR model)',
                    inputs=[
                        {
                            'input_label': None,
                            'input_id': {'type': 'dp-input', 'param': 'immune-period'},
                            'input_value': preset.get('immune_period', 0),
                            'input_step': 0.1,
                            'input_min': 0,
                        }
                    ],
                ),
            ]
        )

    return dbc.ModalBody(modal_elems, class_name='bg-light')


@callback(
    Output('vaccine-parameter-body', 'style'),
    Input('vaccine-model-dropdown', 'value'),
    prevent_initial_call=True,
)
def update_vaccines_modal_body(selected_value):
    if selected_value == 'stockpile-age-risk':
        return {'display': 'block'}
    return {'display': 'none'}


# Vaccine stockpile management callbacks
@callback(
    [
        Output('vaccine-stockpile', 'data'),
        Output('vac-stockpile-table', 'children'),
    ],
    [
        Input('add-vac-stockpile-btn', 'n_clicks'),
        Input({'type': 'remove-vac-stockpile-btn', 'index': ALL}, 'n_clicks'),
    ],
    [
        State('vac-stockpile-day', 'value'),
        State('vac-stockpile-amount', 'value'),
        State('vaccine-stockpile', 'data'),
    ],
    prevent_initial_call=True,
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
                html.Tr(
                    [
                        html.Td(f'{case["day"]}'),
                        html.Td(f'{case["amount"]}'),
                        html.Td(
                            html.Button(
                                'Remove',
                                id={'type': 'remove-vac-stockpile-btn', 'index': case['id']},
                                className='btn btn-sm btn-danger',
                            )
                        ),
                    ]
                )
            )
        table = html.Table(
            [
                html.Thead([html.Tr([html.Th('Day'), html.Th('Amount'), html.Th('Action')])]),
                html.Tbody(table_rows),
            ],
            className='table table-striped',
        )
    else:
        table = html.P('No stockpiles added yet.', className='param-display__empty-state')

    logger.info(f'current_data = {current_data}')
    return current_data, table


@callback(
    Output('model-description-display', 'children'), Input('model-selector-dropdown', 'value')
)
def update_model_description(selected_model):
    """
    Updates the model description when user selects a model.
    """
    if not selected_model:
        return 'Select a model to see its description.'

    # Find the selected model's description
    for model in MODEL_OPTIONS:
        if model['value'] == selected_model:
            return html.Div(
                [
                    html.Span('ℹ️ ', className='model-setup__desc-icon'),
                    html.Span(model['description']),
                ],
            )

    return 'Description not available.'


@callback(
    [
        Output('model-state-status-message', 'children'),
        Output('selected-model-store', 'data'),
        Output('selected-state-store', 'data'),
    ],
    Input('apply-model-state-btn', 'n_clicks'),
    [State('model-selector-dropdown', 'value'), State('state-selector-dropdown', 'value')],
    prevent_initial_call=True,
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
        error_msg = html.Div(
            [
                html.Span('⚠️ ', className='model-setup__status-icon--error'),
                'Please select both a model and a state.',
            ],
            className='model-setup__status--error',
        )
        return error_msg, dash.no_update, dash.no_update

    # Get display names
    model_name = next(
        (m['label'] for m in MODEL_OPTIONS if m['value'] == selected_model), selected_model
    )
    state_name = next(
        (s['label'] for s in STATE_OPTIONS if s['value'] == selected_state), selected_state
    )

    # Create success message
    success_msg = html.Div(
        [
            html.Div(
                [
                    html.Span('✓ ', className='model-setup__status-icon--success'),
                    html.Span('Selection Applied!', className='fw-bold'),
                ]
            ),
            html.Span(
                'Proceed to Step 2 to set your scenario.',
                className='model-setup__status-detail mt-1',
            ),
        ],
        className='model-setup__status--success',
    )

    logger.info(
        f'Model and State selection applied: Model={selected_model}, State={selected_state}'
    )

    return success_msg, selected_model, selected_state


@callback(
    Output('location-assets-store', 'data'),
    Input('apply-model-state-btn', 'n_clicks'),
    State('state-selector-dropdown', 'value'),
    prevent_initial_call=True,
)
def load_assets_for_selected_location(n_clicks, selected_state):
    if not n_clicks or not selected_state:
        return dash.no_update

    try:
        names, mapping, geojson = _load_location_assets(selected_state)
        logger.info(f'Loaded assets for {selected_state}: {len(names)} regions')
        return {'names': names, 'mapping': mapping, 'geojson': geojson}

    except Exception as e:
        logger.error(f'Failed to load assets for {selected_state}: {e}')
        return {'names': [], 'mapping': {}, 'geojson': None}


@callback(Output('initial-location', 'options'), Input('location-assets-store', 'data'))
def update_initial_location_options(location_assets):
    if not location_assets:
        return []

    return [{'label': name, 'value': name} for name in location_assets.get('names', [])]


@callback(
    Output('npi-location', 'options'),
    Input('location-assets-store', 'data'),
)
def update_npi_location_options(location_assets):
    if not location_assets:
        return [{'label': 'Statewide', 'value': 'Statewide'}]

    names = location_assets.get('names', [])
    return [{'label': 'Statewide', 'value': 'Statewide'}] + [
        {'label': n, 'value': n} for n in names
    ]


# Restore UI state after navigation completes
@callback(
    [
        Output('play-pause-btn', 'disabled', allow_duplicate=True),
        Output('play-pause-btn', 'children', allow_duplicate=True),
        Output('play-pause-btn', 'color', allow_duplicate=True),
        Output('timeline-slider', 'disabled', allow_duplicate=True),
        Output('timeline-slider', 'max', allow_duplicate=True),
        Output('timeline-slider', 'value', allow_duplicate=True),
    ],
    Input('main-content', 'children'),
    [
        State('simulation-state', 'data'),
        State('disease-parameters', 'data'),
        State('event-data', 'data'),
    ],
    prevent_initial_call=True,
)
def restore_ui_after_navigation(content, sim_state, disease_params, event_data):
    """Restore play button and timeline after navigation creates new layout"""
    # Only restore if we're on the home page (has play button)
    # Check if content contains home layout by looking for play button
    if not content or not isinstance(content, dict):
        return (
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
        )

    # Restore play button state
    has_disease_params = bool(disease_params)
    is_running = sim_state.get('isRunning', False)
    play_disabled = not has_disease_params

    if is_running:
        play_text = 'Pause'
        play_color = 'warning'
    else:
        play_text = 'Play'
        play_color = 'success'

    # Restore timeline state
    timeline_disabled = not bool(event_data)
    timeline_max = max(30, len(event_data)) if event_data else 30
    timeline_value = len(event_data) - 1 if event_data else 0

    logger.info(
        f'Restoring UI after navigation: play_disabled={play_disabled}, play_text={play_text}, timeline_value={timeline_value}'
    )

    return play_disabled, play_text, play_color, timeline_disabled, timeline_max, timeline_value


@callback(
    Output('sim-scenario-collapse', 'is_open'),
    Output('sim-scenario-caret', 'className'),
    Input('sim-scenario-header', 'n_clicks'),
    State('sim-scenario-collapse', 'is_open'),
)
def toggle_scenario_collapse(n, is_open):
    new_open = (not is_open) if n else is_open
    caret = 'bi bi-caret-up-fill' if new_open else 'bi bi-caret-down-fill'
    return new_open, caret


@callback(
    Output('sim-interventions-collapse', 'is_open'),
    Output('sim-interventions-caret', 'className'),
    Input('sim-interventions-header', 'n_clicks'),
    State('sim-interventions-collapse', 'is_open'),
)
def toggle_interventions_collapse(n, is_open):
    new_open = (not is_open) if n else is_open
    caret = 'bi bi-caret-up-fill' if new_open else 'bi bi-caret-down-fill'
    return new_open, caret


# Modal toggle callbacks - Fixed to prevent auto-opening
@callback(
    Output('disease-params-modal', 'is_open'),
    [
        Input('disease-params-btn', 'n_clicks'),
        Input('disease-params-close', 'n_clicks'),
        Input('disease-params-save', 'n_clicks'),
    ],
    [State('disease-params-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_disease_params_modal(open_click, close_click, save_click, is_open):
    # Check which input triggered the callback
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Only toggle if the disease-params-btn was actually clicked (not just recreated)
    if triggered_id == 'disease-params-btn' and open_click:
        logger.info(
            f'Disease params button clicked: n_clicks={open_click}, current state={is_open}'
        )
        return not is_open
    elif triggered_id in ['disease-params-close', 'disease-params-save'] and (
        close_click or save_click
    ):
        return False

    # For any other case (like button recreation), preserve current state
    return dash.no_update


@callback(
    Output('initial-cases-modal', 'is_open'),
    [
        Input('initial-cases-btn', 'n_clicks'),
        Input('initial-cases-close', 'n_clicks'),
        Input('initial-cases-save', 'n_clicks'),
    ],
    [State('initial-cases-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_initial_cases_modal(open_click, close_click, save_click, is_open):
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'initial-cases-btn' and open_click:
        # .info(f'Initial cases button clicked: n_clicks={open_click}, current state={is_open}')
        return not is_open
    elif triggered_id in ['initial-cases-close', 'initial-cases-save'] and (
        close_click or save_click
    ):
        return False

    return dash.no_update


# Intervention modal toggle callbacks
@callback(
    Output('npi-modal', 'is_open'),
    [Input('npi-btn', 'n_clicks'), Input('npi-close', 'n_clicks'), Input('npi-save', 'n_clicks')],
    [State('npi-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_npi_modal(open_click, close_click, save_click, is_open):
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'npi-btn' and open_click:
        logger.info(f'NPI button clicked: n_clicks={open_click}, current state={is_open}')
        return not is_open
    elif triggered_id in ['npi-close', 'npi-save'] and (close_click or save_click):
        return False

    return dash.no_update


@callback(
    Output('antivirals-modal', 'is_open'),
    [
        Input('antivirals-btn', 'n_clicks'),
        Input('antivirals-close', 'n_clicks'),
        Input('antivirals-save', 'n_clicks'),
    ],
    [State('antivirals-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_antivirals_modal(open_click, close_click, save_click, is_open):
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'antivirals-btn' and open_click:
        logger.info(f'Antivirals button clicked: n_clicks={open_click}, current state={is_open}')
        return not is_open
    elif triggered_id in ['antivirals-close', 'antivirals-save'] and (close_click or save_click):
        return False

    return dash.no_update


@callback(
    Output('vaccines-modal', 'is_open'),
    [
        Input('vaccines-btn', 'n_clicks'),
        Input('vaccines-close', 'n_clicks'),
        Input('vaccines-save', 'n_clicks'),
    ],
    [State('vaccines-modal', 'is_open')],
    prevent_initial_call=True,
)
def toggle_vaccines_modal(open_click, close_click, save_click, is_open):
    if not ctx.triggered:
        return dash.no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'vaccines-btn' and open_click:
        logger.info(f'Vaccines button clicked: n_clicks={open_click}, current state={is_open}')
        return not is_open
    elif triggered_id in ['vaccines-close', 'vaccines-save'] and (close_click or save_click):
        return False

    return dash.no_update


# Preset scenario loading callback
@callback(
    Output('disease-preset-store', 'data'),
    Input({'type': 'dp-dropdown', 'param': 'preset'}, 'value'),
    State('model-selector-dropdown', 'value'),
    prevent_initial_call=True,
)
def load_preset_scenario(preset_key, selected_value):
    if not preset_key or not selected_value:
        return {}
    scenario_prefix = selected_value.split('-')[0]
    if preset_key in PRESET_SCENARIOS.get(scenario_prefix, {}):
        return PRESET_SCENARIOS[scenario_prefix][preset_key]
    return {}


@callback(
    Output('initial-cases-save', 'disabled'),
    Output('initial-cases-footer-note', 'style'),
    Input('initial-cases-data', 'data'),
)
def update_initial_cases_footer(cases):
    has_cases = bool(cases)
    return not has_cases, {} if not has_cases else {'display': 'none'}


_NO_FEEDBACK = {'display': 'none'}
_SHOW_FEEDBACK = {'display': 'block'}
_CLEAR_VALIDATION = (
    '',  # initial-location-wrapper className
    _NO_FEEDBACK,  # initial-location-feedback style
    '',  # initial-cases-count-wrapper className
    _NO_FEEDBACK,  # initial-cases-count-feedback style
    '',  # initial-age-group-wrapper className
    _NO_FEEDBACK,  # initial-age-group-feedback style
)


@callback(
    Output('initial-location-wrapper', 'className', allow_duplicate=True),
    Output('initial-location-feedback', 'style', allow_duplicate=True),
    Input('initial-location', 'value'),
    prevent_initial_call=True,
)
def clear_location_validation(value):
    return ('', _NO_FEEDBACK) if value else dash.no_update


@callback(
    Output('initial-cases-count-wrapper', 'className', allow_duplicate=True),
    Output('initial-cases-count-feedback', 'style', allow_duplicate=True),
    Input('initial-cases-count', 'value'),
    prevent_initial_call=True,
)
def clear_count_validation(value):
    if value and value >= 1:
        return '', _NO_FEEDBACK
    return dash.no_update, dash.no_update


@callback(
    Output('initial-age-group-wrapper', 'className', allow_duplicate=True),
    Output('initial-age-group-feedback', 'style', allow_duplicate=True),
    Input('initial-age-group', 'value'),
    prevent_initial_call=True,
)
def clear_age_group_validation(value):
    return ('', _NO_FEEDBACK) if value else dash.no_update


@callback(
    Output('initial-location-wrapper', 'className', allow_duplicate=True),
    Output('initial-location-feedback', 'style', allow_duplicate=True),
    Output('initial-cases-count-wrapper', 'className', allow_duplicate=True),
    Output('initial-cases-count-feedback', 'style', allow_duplicate=True),
    Output('initial-age-group-wrapper', 'className', allow_duplicate=True),
    Output('initial-age-group-feedback', 'style', allow_duplicate=True),
    Input('initial-cases-modal', 'is_open'),
    prevent_initial_call=True,
)
def reset_validation_on_modal_open(is_open):
    if is_open:
        return '', _NO_FEEDBACK, '', _NO_FEEDBACK, '', _NO_FEEDBACK
    return [dash.no_update] * 6


# Initial cases management callbacks
@callback(
    [
        Output('initial-cases-data', 'data'),
        Output('initial-cases-table', 'children'),
        Output('play-pause-btn', 'disabled', allow_duplicate=True),
        Output('initial-location-wrapper', 'className'),
        Output('initial-location-feedback', 'style'),
        Output('initial-cases-count-wrapper', 'className'),
        Output('initial-cases-count-feedback', 'style'),
        Output('initial-age-group-wrapper', 'className'),
        Output('initial-age-group-feedback', 'style'),
    ],
    [
        Input('add-initial-case-btn', 'n_clicks'),
        Input({'type': 'remove-case-btn', 'index': ALL}, 'n_clicks'),
    ],
    [
        State('initial-location', 'value'),
        State('initial-cases-count', 'value'),
        State('initial-age-group', 'value'),
        State('initial-cases-data', 'data'),
        State('location-assets-store', 'data'),
        State('disease-parameters', 'data'),
    ],
    prevent_initial_call=True,
)
def manage_initial_cases(
    add_clicks,
    remove_clicks,
    location,
    cases_count,
    age_group,
    current_data,
    location_assets,
    disease_params,
):
    triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None

    mapping = (location_assets or {}).get('mapping', {})

    current_data = current_data or []

    if 'add-initial-case-btn' in triggered_id:
        loc_invalid = not location
        count_invalid = not cases_count or cases_count < 1
        age_invalid = not age_group
        if loc_invalid or count_invalid or age_invalid:
            table = _build_cases_table(current_data)
            play_disabled = not (bool(disease_params) and bool(current_data))
            return (
                current_data,
                table,
                play_disabled,
                'dropdown-invalid' if loc_invalid else '',
                _SHOW_FEEDBACK if loc_invalid else _NO_FEEDBACK,
                'dropdown-invalid' if count_invalid else '',
                _SHOW_FEEDBACK if count_invalid else _NO_FEEDBACK,
                'dropdown-invalid' if age_invalid else '',
                _SHOW_FEEDBACK if age_invalid else _NO_FEEDBACK,
            )

    if 'add-initial-case-btn' in triggered_id:
        # Validation already returned early above if invalid; reaching here means valid.
        fips_id = mapping.get(location, '0')
        age_group_id = AGE_GROUP_MAPPING.get(age_group, '0')
        current_data.append(
            {
                'id': len(current_data),
                'location': location,
                'fips_id': fips_id,
                'cases': cases_count,
                'age_group': age_group,
                'age_group_id': age_group_id,
            }
        )

    elif 'remove-case-btn' in triggered_id:
        import re

        match = re.search(r'"index":(\d+)', triggered_id)
        if match:
            remove_index = int(match.group(1))
            current_data = [case for case in current_data if case['id'] != remove_index]

    table = _build_cases_table(current_data)
    play_disabled = not (bool(disease_params) and bool(current_data))
    return (current_data, table, play_disabled, *_CLEAR_VALIDATION)


def _build_cases_table(current_data):
    if not current_data:
        return html.P('No initial cases added yet.', className='param-display__empty-state')
    rows = [
        html.Tr(
            [
                html.Td(case['location']),
                html.Td(f'{case["cases"]} aged {case["age_group"]}'),
                html.Td(
                    html.Button(
                        'Remove',
                        id={'type': 'remove-case-btn', 'index': case['id']},
                        className='btn btn-sm btn-danger',
                    )
                ),
            ]
        )
        for case in current_data
    ]
    return html.Table(
        [
            html.Thead([html.Tr([html.Th('Location'), html.Th('Cases'), html.Th('Action')])]),
            html.Tbody(rows),
        ],
        className='table table-striped',
    )


# Disease parameters save callback
@callback(
    [
        Output('disease-parameters', 'data'),
        Output('scenario-content', 'children', allow_duplicate=True),
        Output('play-pause-btn', 'disabled', allow_duplicate=True),
    ],
    Input('disease-params-save', 'n_clicks'),
    [
        State({'type': 'dp-input', 'param': ALL}, 'value'),
        State('initial-cases-data', 'data'),
        State('selected-model-store', 'data'),
    ],
    prevent_initial_call=True,
)
def save_disease_parameters(n_clicks, dp_input_values, initial_cases, selected_model):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update

    # Build a dict of param -> value from the pattern-matched inputs
    p = {}
    for state_info, value in zip(ctx.states_list[0], dp_input_values):
        p[state_info['id']['param']] = value

    nu_defaults = [0.000022319, 0.000040975, 0.000083729, 0.000061809, 0.000008978]
    disease_params = {
        'scenario_name': p.get('scenario-name') or 'Custom Scenario',
        'R0': p.get('reproduction-number') or 1.2,
        'tau': p.get('latent-period') or 1.2,
        'kappa': p.get('asymptomatic-period') or 1.9,
        'gamma': p.get('symptomatic-period') or 4.1,
        'chi': 1.0,
        'rho': 0.39,
        'nu': [
            p.get('cfr-0-4') or nu_defaults[0],
            p.get('cfr-5-24') or nu_defaults[1],
            p.get('cfr-25-49') or nu_defaults[2],
            p.get('cfr-50-64') or nu_defaults[3],
            p.get('cfr-65-plus') or nu_defaults[4],
        ],
        'sigma': [
            p.get('sigma-0-4') or 1,
            p.get('sigma-5-24') or 1,
            p.get('sigma-25-49') or 1,
            p.get('sigma-50-64') or 1,
            p.get('sigma-65-plus') or 1,
        ],
        'infectious_period': p.get('infectious-period') or 7,
        'immune_period': p.get('immune-period') or 0,
        'model_type': selected_model,
    }

    logger.info('saved disease parameters = ')
    logger.info(disease_params)

    content = create_scenario_display(disease_params, initial_cases)
    play_disabled = not (bool(disease_params) and bool(initial_cases) and len(initial_cases) > 0)

    return disease_params, content, play_disabled


# Save intervention callbacks
# NPI callback
@callback(
    [Output('npi-data', 'data'), Output('npi-table', 'children')],
    [Input('add-npi-btn', 'n_clicks'), Input({'type': 'remove-npi-btn', 'index': ALL}, 'n_clicks')],
    [
        State('npi-name', 'value'),
        State('npi-start', 'value'),
        State('npi-duration', 'value'),
        State('npi-eff-0-4', 'value'),
        State('npi-eff-5-24', 'value'),
        State('npi-eff-25-49', 'value'),
        State('npi-eff-50-64', 'value'),
        State('npi-eff-65-plus', 'value'),
        State('npi-location', 'value'),
        State('npi-data', 'data'),
    ],
    prevent_initial_call=True,
)
def manage_npis(
    add_clicks,
    remove_clicks,
    name,
    start,
    duration,
    eff_0_4,
    eff_5_24,
    eff_25_49,
    eff_50_64,
    eff_65_plus,
    location,
    current_npi_data,
):

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

        current_npi_data.append(
            {
                'name': name,
                'start': int(start),
                'duration': int(duration),
                'effectiveness': effectiveness,
                'location': location,
            }
        )

        return current_npi_data, _render_npi_table(current_npi_data)

    # ----- Remove -----
    if isinstance(trig, dict) and trig.get('type') == 'remove-npi-btn':
        idx = trig.get('index')
        if isinstance(idx, int) and 0 <= idx < len(current_npi_data):
            current_npi_data.pop(idx)

        return current_npi_data, _render_npi_table(current_npi_data)

    # Fallback: nothing changed
    return current_npi_data, _render_npi_table(current_npi_data)


@callback(
    [
        Output('scenario-content', 'children', allow_duplicate=True),
        Output('interventions-content', 'children', allow_duplicate=True),
    ],
    [
        Input('disease-parameters', 'data'),
        Input('initial-cases-data', 'data'),
        Input('npi-data', 'data'),
        Input('antiviral-data', 'data'),
        Input('vaccine-data', 'data'),
        Input('vaccine-stockpile', 'data'),
    ],
    prevent_initial_call=True,
)
def refresh_displayed_parameters(
    disease_params,
    initial_cases,
    npi_data,
    antiviral_data,
    vaccine_data,
    vaccine_stockpile,
):
    scenario = create_scenario_display(disease_params or {}, initial_cases or [])
    interventions = create_interventions_display(
        npi_data or [], antiviral_data or {}, vaccine_data or {}, vaccine_stockpile or []
    )
    return scenario, interventions


# Antiviral callback
@callback(
    [
        Output('antiviral-effectiveness', 'value'),
        Output('antiviral-wastage', 'value'),
        Output('antiviral-stockpile-day', 'value'),
        Output('antiviral-stockpile-amount', 'value'),
    ],
    Input('antivirals-modal', 'is_open'),
    State('antiviral-data', 'data'),
    prevent_initial_call=True,
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
    [
        Output('antiviral-data', 'data'),
        Output('antivirals-enabled', 'data'),
        Output('interventions-content', 'children', allow_duplicate=True),
    ],
    Input('antivirals-save', 'n_clicks'),
    [
        State('antiviral-effectiveness', 'value'),
        State('antiviral-wastage', 'value'),
        State('antiviral-stockpile-day', 'value'),
        State('antiviral-stockpile-amount', 'value'),
        State('npi-data', 'data'),
        State('vaccine-data', 'data'),
        State('vaccine-stockpile', 'data'),
    ],
    prevent_initial_call=True,
)
def save_antivirals(
    n_clicks,
    effectiveness,
    wastage,
    stockpile_day,
    stockpile_amount,
    npi_data,
    vaccine_data,
    vaccine_stockpile,
):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update

    antiviral_data = {
        'effectiveness': 0.15 if effectiveness is None else effectiveness,
        'wastage_factor': 60 if wastage is None else wastage,
        'stockpile_day': 50 if stockpile_day is None else stockpile_day,
        'stockpile_amount': 10000 if stockpile_amount is None else stockpile_amount,
    }

    content = create_interventions_display(
        npi_data or [], antiviral_data, vaccine_data or {}, vaccine_stockpile or []
    )
    return antiviral_data, True, content


@callback(
    [
        Output('vaccine-data', 'data'),
        Output('vaccines-enabled', 'data'),
        Output('interventions-content', 'children', allow_duplicate=True),
    ],
    Input('vaccines-save', 'n_clicks'),
    [
        State('vaccine-model-dropdown', 'value'),
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
        State('npi-data', 'data'),
        State('antiviral-data', 'data'),
    ],
    prevent_initial_call=True,
)
def save_vaccines(
    n_clicks,
    vaccine_model,
    priority_groups,
    capacity,
    effectiveness_lag,
    vac_eff_0,
    vac_eff_1,
    vac_eff_2,
    vac_eff_3,
    vac_eff_4,
    vac_adh_0,
    vac_adh_1,
    vac_adh_2,
    vac_adh_3,
    vac_adh_4,
    vaccine_stockpile,
    npi_data,
    antiviral_data,
):
    if not n_clicks:
        return [dash.no_update] * 3

    arpgs = [
        'vac-arpg-0-4',
        'vac-arpg-5-17',
        'vac-arpg-18-49',
        'vac-arpg-50-64',
        'vac-arpg-65-plus',
    ]

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

    content = create_interventions_display(
        npi_data or [], antiviral_data or {}, vaccine_data, vaccine_stockpile
    )
    return vaccine_data, True, content


# Reset callback - connects to Django backend
@callback(
    Output('url', 'href'),
    Input('reset-btn', 'n_clicks'),
    State('simulation-state', 'data'),
    prevent_initial_call=True,
)
def reset_simulation(n_clicks, sim_state):
    if n_clicks:
        logger.info('Resetting simulation...')

        if sim_state.get('isRunning'):
            try:
                task_id = sim_state.get('taskId')
                if task_id:
                    requests.get(f'{API_BASE_URL}/api/delete/{task_id}')
            except:
                pass

        try:
            response = requests.get(f'{API_BASE_URL}/api/reset')
            logger.info(f'Reset response status: {response.status_code}')
        except:
            pass

        return '/'

    return dash.no_update


# Play/Pause simulation callback - connects to Django backend
@callback(
    [
        Output('simulation-state', 'data'),
        Output('play-pause-btn', 'children'),
        Output('play-pause-btn', 'color'),
        Output('play-pause-btn', 'disabled', allow_duplicate=True),
        Output('simulation-interval', 'disabled'),
        Output('timeline-slider', 'disabled', allow_duplicate=True),
    ],
    Input('play-pause-btn', 'n_clicks'),
    [
        State('simulation-state', 'data'),
        State('disease-parameters', 'data'),
        State('initial-cases-data', 'data'),
        State('npi-data', 'data'),
        State('antiviral-data', 'data'),
        State('vaccine-data', 'data'),
        State('vaccine-stockpile', 'data'),
        State('antivirals-enabled', 'data'),
        State('vaccines-enabled', 'data'),
        State('selected-model-store', 'data'),
        State('selected-state-store', 'data'),
    ],
    prevent_initial_call=True,
)
def toggle_simulation(
    n_clicks,
    sim_state,
    disease_params,
    initial_cases,
    npi_data,
    antiviral_data,
    vaccine_data,
    vaccine_stockpile,
    antivirals_enabled,
    vaccines_enabled,
    selected_model,
    selected_state,
):
    if n_clicks and disease_params:
        is_running = sim_state.get('isRunning', False)

        if not is_running:
            # Start simulation - call Django backend exactly like React
            try:
                logger.info('Starting new simulation...')
                logger.info(
                    f'Using Model: {selected_model}, State: {selected_state}'
                )  # NEW: Log selection

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
                    'nu': ','.join(map(str, disease_params.get('nu', [0, 0, 0, 0, 0]))),
                    'sigma': ','.join(map(str, disease_params.get('sigma', [1, 1, 1, 1, 1]))),
                    'infectious_period': disease_params.get('infectious_period', 14),
                    'immune_period': disease_params.get('immune_period', 0),
                }

                # Add initial cases - use provided cases or default to Harris County
                initial_infected = []
                if initial_cases:
                    for case in initial_cases:
                        initial_infected.append(
                            {
                                'county': case['fips_id'],
                                'infected': case['cases'],
                                'age_group': case['age_group_id'],
                            }
                        )

                payload['initial_infected'] = json.dumps(initial_infected)

                # Add default empty values for required fields
                # baseline defaults
                payload.update(
                    {
                        'npis': json.dumps([]),
                        'antiviral_model': json.dumps({}),
                        'vaccine_model': json.dumps({}),
                    }
                )

                # Add NPIs
                if npi_data:
                    npis = []
                    for npi in npi_data:
                        npis.append(
                            {
                                'type': npi['name'],
                                'day': npi['start'],
                                'duration': npi['duration'],
                                'effectiveness': npi['effectiveness'],
                                'location': npi['location'],
                            }
                        )
                    payload['npis'] = json.dumps(npis)

                # Antivirals only if enabled
                # if antivirals_enabled and antiviral_data:
                #    payload.update({
                #        'antiviral_effectiveness': antiviral_data['effectiveness'],
                #        'antiviral_stockpile': antiviral_data['stockpile_amount'],
                #        'antiviral_wastage_factor': antiviral_data['wastage_factor'] / 365.0
                #    })

                # Add vaccines
                if vaccines_enabled and vaccine_data:
                    payload.update(
                        {
                            'vaccine_model': vaccine_data['vaccine_model'],
                            'vaccine_priority_groups': json.dumps(vaccine_data['priority_groups']),
                            'vaccine_capacity': vaccine_data['capacity'],
                            'vaccine_effectiveness_lag': vaccine_data['effectiveness_lag'],
                            'vaccine_effectiveness': json.dumps(vaccine_data['effectiveness']),
                            'vaccine_adherence': json.dumps(vaccine_data['adherence']),
                        }
                    )

                    payload.update({'vaccine_stockpile': json.dumps(vaccine_stockpile)})

                # Call Django API to create simulation
                logger.info(f'Sending payload to API: {payload}')
                response = requests.post(f'{API_BASE_URL}/api/pet/', json=payload)
                logger.info(
                    f'API response status: {response.status_code}, content: {response.text}'
                )
                if response.status_code == 201:
                    sim_id = response.json().get('id')
                    logger.info(f'Simulation created with ID: {sim_id}')

                    # Start simulation
                    run_response = requests.get(f'{API_BASE_URL}/api/pet/{sim_id}/run')
                    logger.info(
                        f'Run response status: {run_response.status_code}, content: {run_response.text}'
                    )

                    if run_response.status_code in [200, 202]:
                        task_id = run_response.json().get('task_id')
                        logger.info(f'Simulation started with task ID: {task_id}')

                        new_state = {
                            **sim_state,
                            'isRunning': True,
                            'currentIndex': 0,
                            'id': sim_id,
                            'taskId': task_id,
                        }

                        return new_state, 'Pause', 'warning', False, False, False
                    else:
                        logger.error(f'Failed to start simulation run: {run_response.status_code}')
                else:
                    logger.error(f'Failed to create simulation: {response.status_code}')

                # If API call failed, show error but don't start
                return sim_state, 'Play', dash.no_update, False, True, True

            except Exception as e:
                logger.error(f'Error starting simulation: {e}')
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
            return new_state, 'Play', 'success', False, True, False

    return (
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
        dash.no_update,
    )


# Simulation data fetching callback - gets real data from Django backend
@callback(
    [
        Output('event-data', 'data'),
        Output('timeline-slider', 'max'),
        Output('timeline-slider', 'value'),
    ],
    Input('simulation-interval', 'n_intervals'),
    [State('simulation-state', 'data'), State('event-data', 'data')],
    prevent_initial_call=True,
)
def fetch_simulation_data(n_intervals, sim_state, event_data):
    if sim_state.get('isRunning', False):
        current_day = len(event_data)  # Start from day 0

        try:
            # Fetch real data from Django backend
            logger.info(f'Fetching data for day {current_day}')
            response = requests.get(f'{API_BASE_URL}/api/output/{current_day}')
            logger.info(
                f'Output API response: {response.status_code}, content: {response.text[:200]}'
            )

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
                    'totalDeceased': 0,
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
                            county_population = (
                                sum(compartment_summary.values()) if compartment_summary else 1
                            )
                            infected_percent = (
                                (infected / county_population * 100) if county_population > 0 else 0
                            )
                            deceased_percent = (
                                (deceased / county_population * 100) if county_population > 0 else 0
                            )

                            county_info = {
                                'fips': fips_id,
                                'infected': infected,
                                'deceased': deceased,
                                'infectedPercent': infected_percent,
                                'deceasedPercent': deceased_percent,
                            }
                            day_data['counties'].append(county_info)

                # Set calculated totals
                day_data.update(
                    {
                        'totalSusceptible': total_S,
                        'totalExposed': total_E,
                        'totalAsymptomaticCount': total_A,
                        'totalTreatableCount': total_T,
                        'totalInfectedCount': total_I,
                        'totalRecoveredCount': total_R,
                        'totalDeceased': total_D,
                    }
                )

                updated_event_data = event_data + [day_data]
                logger.info(f'Added day {current_day} data, total days: {len(updated_event_data)}')
                return updated_event_data, len(updated_event_data), len(updated_event_data) - 1
            elif response.status_code == 404 or 'not calculated' in response.text:
                # Day not ready yet, don't increment but keep checking
                logger.info(f'Day {current_day} not ready yet')
                return (
                    event_data,
                    max(30, len(event_data)),
                    len(event_data) - 1 if event_data else 0,
                )

        except Exception as e:
            logger.error(f'API fetch failed: {e}')

    return event_data, max(30, len(event_data)), len(event_data) - 1 if event_data else 0


# Real data visualization callbacks


@callback(
    Output('spread-map', 'figure'),
    [
        Input('event-data', 'data'),
        Input('timeline-slider', 'value'),
        Input('view-toggle', 'value'),
        Input('location-assets-store', 'data'),
    ],
    State('selected-model-store', 'data'),
)
def update_map(event_data, timeline_value, view_type, location_assets, selected_model):
    """Update map with county-level choropleth visualization"""

    geojson = location_assets.get('geojson') if location_assets else None

    # Show empty map with state boundaries if no simulation data yet
    if geojson and (not event_data or len(event_data) == 0):
        logger.info('Displaying empty map with state boundaries')
        return _create_empty_state_map(geojson)

    # DEBUG LOGGING
    logger.info(
        f'map debug → '
        f'event_days={len(event_data) if event_data else 0}, '
        f'timeline={timeline_value}, '
        f'geojson_loaded={bool(geojson)}'
    )

    return _create_jurisdiction_choropleth(
        event_data, timeline_value, view_type, geojson, selected_model
    )


@callback(
    Output('line-chart', 'figure'),
    [Input('event-data', 'data'), Input('timeline-slider', 'value')],
    State('selected-model-store', 'data'),
)
def update_chart(event_data, timeline_value, selected_model):
    if not event_data:
        fig = go.Figure()
        fig.update_layout(
            title='Epidemic Curve - No Data Available',
            xaxis_title='Day',
            yaxis_title='Population Count',
            height=300,
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
    model = (selected_model or '').lower()
    if model.startswith('seir') or model.startswith('seirs'):
        # SEIR
        series = [
            ('Susceptible', susceptible),
            ('Exposed', exposed),
            ('Infectious', infected),
            ('Recovered', recovered),
        ]
    else:
        # SEATIRD
        series = [
            ('Susceptible', susceptible),
            ('Exposed', exposed),
            ('Asymptomatic Infectious', asymptomatic),
            ('Treatable Infectious', treatable),
            ('Symptomatic Infectious', infected),
            ('Recovered', recovered),
            ('Deceased', deceased),
        ]

    # Add traces for SEATIRD compartments
    COLOR_MAP = {
        'Susceptible': 'blue',
        'Exposed': 'orange',
        'Asymptomatic Infectious': 'gold',
        'Treatable Infectious': 'purple',
        'Symptomatic Infectious': 'red',
        'Infectious': 'red',
        'Recovered': 'green',
        'Deceased': 'black',
    }
    fig = go.Figure()
    for name, y in series:
        fig.add_trace(go.Scatter(x=days, y=y, name=name, line=dict(color=COLOR_MAP.get(name))))

    # Add vertical line for current day
    if timeline_value is not None and timeline_value < len(days):
        fig.add_vline(
            x=timeline_value,
            line_dash='dash',
            line_color='gray',
            annotation_text=f'Day {timeline_value}',
        )

    fig.update_layout(
        title=dict(
            # text="Epidemic Curve", # remove title to make space for legend
            y=0.96,
            yanchor='top',
            pad=dict(t=5),
        ),
        xaxis_title='Day',
        yaxis_title='Population Count',
        height=300,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=40, r=40, t=60, b=70),
        hovermode='x unified',
    )

    return fig


@callback(
    Output('county-table-sort', 'data', allow_duplicate=True),
    Input({'type': 'sort-btn', 'col': ALL}, 'n_clicks'),
    State('county-table-sort', 'data'),
    prevent_initial_call=True,
)
def handle_sort_click(sort_clicks, sort_state):
    sort_state = sort_state or {'col': 'infected', 'dir': 'desc'}
    trig = ctx.triggered_id
    if isinstance(trig, dict) and trig.get('type') == 'sort-btn':
        col = trig['col']
        if sort_state.get('col') == col:
            sort_state['dir'] = 'asc' if sort_state['dir'] == 'desc' else 'desc'
        else:
            sort_state = {'col': col, 'dir': 'desc'}
    return sort_state


@callback(
    Output('spread-table', 'children'),
    [
        Input('event-data', 'data'),
        Input('timeline-slider', 'value'),
        Input('view-toggle', 'value'),
        Input('location-assets-store', 'data'),
        Input('county-search', 'value'),
        Input('county-table-sort', 'data'),
    ],
    State('selected-model-store', 'data'),
)
def update_table(
    event_data,
    timeline_value,
    view_type,
    location_assets,
    search_text,
    sort_state,
    selected_model,
):
    sort_state = sort_state or {'col': 'infected', 'dir': 'desc'}

    model = (selected_model or '').lower()
    right_col_label = (
        'Recovered' if model.startswith('seir') or model.startswith('seirs') else 'Deceased'
    )

    if not event_data or timeline_value is None or timeline_value >= len(event_data):
        return html.P('No data available', className='param-display__empty-state')

    current_data = event_data[timeline_value]
    counties_data = current_data.get('counties', [])
    if not counties_data:
        return html.P('No county data available', className='param-display__empty-state')

    location_assets = location_assets or {}
    mapping = location_assets.get('mapping', {})  # name -> geoid (string)

    # Invert mapping once: geoid -> name
    id_to_name = {str(geoid): name for name, geoid in mapping.items() if str(name).lower() != 'all'}

    # Build DataFrame
    inf_key = 'infectedPercent' if view_type == 'percent' else 'infected'
    dec_key = 'deceasedPercent' if view_type == 'percent' else 'deceased'

    records = []
    for county in counties_data:
        geoid = str(county.get('fips', '')).strip()
        if not geoid:
            continue
        if len(geoid) == 4:  # leading zero lost for some states
            geoid = geoid.zfill(5)
        records.append(
            {
                'name': id_to_name.get(geoid) or geoid,
                'infected_num': float(county.get(inf_key, 0)),
                'deceased_num': float(county.get(dec_key, 0)),
            }
        )

    df = pd.DataFrame(records)

    if df.empty:
        return html.P('No county data available', className='param-display__empty-state')

    # --- search
    if search_text:
        q = search_text.strip().lower()
        mask = df.apply(
            lambda r: q in f'{r["name"]} {r["infected_num"]} {r["deceased_num"]}'.lower(),
            axis=1,
        )
        df = df[mask]

    if df.empty:
        return html.P('No county data available', className='param-display__empty-state')

    # --- sort
    sort_col = {'name': 'name', 'infected': 'infected_num', 'deceased': 'deceased_num'}[
        sort_state['col']
    ]
    df = df.sort_values(sort_col, ascending=(sort_state['dir'] == 'asc'))

    # --- format display columns
    if view_type == 'percent':
        df['infected_disp'] = df['infected_num'].map(lambda x: f'{x:.1f}%')
        df['deceased_disp'] = df['deceased_num'].map(lambda x: f'{x:.1f}%')
    else:
        df['infected_disp'] = df['infected_num'].map(lambda x: f'{math.floor(x):,}')
        df['deceased_disp'] = df['deceased_num'].map(lambda x: f'{math.floor(x):,}')

    # --- header with clickable sort buttons (minimal styling)
    arrow_loc = (
        '▲'
        if sort_state['col'] == 'name' and sort_state['dir'] == 'asc'
        else ('▼' if sort_state['col'] == 'name' else '')
    )
    arrow_inf = (
        '▼'
        if sort_state['col'] == 'infected' and sort_state['dir'] == 'desc'
        else ('▲' if sort_state['col'] == 'infected' else '')
    )
    arrow_dec = (
        '▼'
        if sort_state['col'] == 'deceased' and sort_state['dir'] == 'desc'
        else ('▲' if sort_state['col'] == 'deceased' else '')
    )

    header = html.Thead(
        html.Tr(
            [
                html.Th(
                    html.Button(
                        f'Location {arrow_loc}',
                        id={'type': 'sort-btn', 'col': 'name'},
                        n_clicks=0,
                        className='sim-layout__sort-btn',
                    )
                ),
                html.Th(
                    html.Button(
                        f'Infectious {arrow_inf}',
                        id={'type': 'sort-btn', 'col': 'infected'},
                        n_clicks=0,
                        className='sim-layout__sort-btn',
                    )
                ),
                html.Th(
                    html.Button(
                        f'{right_col_label} {arrow_dec}',
                        id={'type': 'sort-btn', 'col': 'deceased'},
                        n_clicks=0,
                        className='sim-layout__sort-btn',
                    )
                ),
            ]
        )
    )

    body = html.Tbody(
        [
            html.Tr([html.Td(r.name), html.Td(r.infected_disp), html.Td(r.deceased_disp)])
            for r in df.itertuples()
        ]
    )

    table = dbc.Table(
        [header, body],
        bordered=True,
        hover=True,
        striped=True,
        responsive=False,
        className='w-100 sim-layout__county-table',
    )

    return table
