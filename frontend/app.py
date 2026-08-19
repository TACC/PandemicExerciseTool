import glob
import json
import logging
import math
import os
import subprocess

import dash
from dash import dcc, html, Input, Output, State, callback, ctx, ALL, page_container
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import requests

# from user_guide import create_userguide_layout
from constants import MODEL_OPTIONS, PRESET_SCENARIOS, AGE_GROUPS, AGE_GROUP_MAPPING, VACCINE_MODELS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get version from environment
result = subprocess.run(
    'git symbolic-ref -q --short HEAD || git describe --tags --exact-match',
    shell=True,
    capture_output=True,
)
version = result.stdout.decode('utf-8').strip() if result.stdout else 'Unknown'

# Initialize Dash app with external CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], use_pages=True)
app.title = f'epiENGAGE - Interactive Outbreak Simulator v-{version}'
app.config.suppress_callback_exceptions = True


# ============================================================================
# APP LAYOUT
# ============================================================================
app.layout = html.Div(
    [
        # Stores for state management
        dcc.Store(
            id='simulation-state',
            data={'isRunning': False, 'currentIndex': 0, 'taskId': None, 'id': None},
        ),
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
        dcc.Store(id='disease-preset-store', data={}),
        dcc.Interval(id='simulation-interval', interval=1000, disabled=True),
        # Stores for Model and State Selection
        dcc.Store(id='selected-model-store', data='seirs-deterministic'),
        dcc.Store(id='selected-state-store', data='Alabama'),
        dcc.Store(id='location-assets-store', data={}),
        # Header
        html.Nav(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Img(
                                            src='/assets/epiengage_logo_darkblue.jpg',
                                            style={'width': '60px', 'height': '60px'},
                                            className='align-top header-logo',
                                        ),
                                        html.Span(
                                            'epiENGAGE',
                                            className='app-header__name',
                                        ),
                                    ],
                                    style={'display': 'flex', 'alignItems': 'center'},
                                ),
                                html.Div(
                                    [
                                        html.Ul(
                                            [
                                                html.Li(
                                                    [
                                                        html.A(
                                                            'Home',
                                                            id='nav-home',
                                                            href='/',
                                                            className='app-header__nav-link app-header__nav-link--active',
                                                        )
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.A(
                                                            'User Guide',
                                                            id='nav-userguide',
                                                            href='/guide',
                                                            className='app-header__nav-link',
                                                        )
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.A(
                                                            'About Us',
                                                            id='nav-about',
                                                            href='/about',
                                                            className='app-header__nav-link',
                                                        )
                                                    ]
                                                ),
                                            ],
                                            style={
                                                'listStyle': 'none',
                                                'display': 'flex',
                                                'margin': '0',
                                                'padding': '0',
                                            },
                                        )
                                    ],
                                    style={'flex': '1', 'textAlign': 'center'},
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            f'Interactive Outbreak Simulator v-{version}',
                                            style={'color': 'white'},
                                        )
                                    ]
                                ),
                            ],
                            style={
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'space-between',
                                'width': '100%',
                                'padding': '0 20px',
                            },
                        )
                    ],
                    className='container-fluid',
                )
            ],
            style={
                'backgroundColor': '#102c41',
                'position': 'fixed',
                'top': '0',
                'width': '100%',
                'zIndex': '1000',
                'padding': '10px 0',
            },
        ),
        # Main content area
        dbc.Container(
            [
                html.Div(page_container, style={'marginTop': '80px'}),
                # html.Div(id='main-content'),
            ],
            fluid=True,
            class_name='base-container'
        ),
    ]
)


# Navigation callback
# @callback(
#     [
#         Output('main-content', 'children'),
#         Output('nav-home', 'className'),
#         Output('nav-userguide', 'className'),
#         Output('disease-params-modal', 'is_open', allow_duplicate=True),
#         Output('initial-cases-modal', 'is_open', allow_duplicate=True),
#         Output('npi-modal', 'is_open', allow_duplicate=True),
#         Output('antivirals-modal', 'is_open', allow_duplicate=True),
#         Output('vaccines-modal', 'is_open', allow_duplicate=True),
#     ],
#     [Input('nav-home', 'n_clicks'), Input('nav-userguide', 'n_clicks')],
#     prevent_initial_call=True,
# )
# def navigate_pages(home_clicks, userguide_clicks):
#     triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'nav-home'

#     if triggered_id == 'nav-userguide':
#         return (
#             create_userguide_layout(),
#             'tab-button',
#             'tab-button active',
#             False,
#             False,
#             False,
#             False,
#             False,
#         )
#     else:
#         return (
#             create_home_layout(),
#             'tab-button active',
#             'tab-button',
#             False,
#             False,
#             False,
#             False,
#             False,
#         )


# Expose server for deployment
server = app.server

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8051)
