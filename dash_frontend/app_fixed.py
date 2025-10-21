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
        
        # Extract the array content
        start = content.find('[')
        end = content.rfind(']') + 1
        counties_str = content[start:end]
        
        # Parse as JSON
        counties_list = json.loads(counties_str)
        
        # Convert to the format used in React
        return counties_list
    except Exception as e:
        logger.warning(f"Could not load Texas counties: {e}")
        # Use the same mock data as React would have
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
     Output('simulation-interval', 'disabled')],
    Input('play-pause-btn', 'n_clicks'),
    [State('simulation-state', 'data'),
     State('has-set-scenario', 'data')],
    prevent_initial_call=True
)
def toggle_simulation(n_clicks, sim_state, has_scenario):
    if n_clicks and has_scenario:
        is_running = sim_state.get('isRunning', False)
        
        if not is_running:
            # Start simulation
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
            return new_state, 'Pause', button_style, False
        else:
            # Pause simulation
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
            return new_state, 'Play', button_style, True
    
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

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
    return create_empty_map()

# Chart callback
@callback(
    Output('line-chart', 'figure'),
    Input('event-data', 'data')
)
def update_chart(event_data):
    return create_empty_chart()

# Table callback
@callback(
    Output('spread-table', 'children'),
    [Input('event-data', 'data'),
     Input('timeline-slider', 'value'),
     Input('view-toggle', 'value')]
)
def update_table(event_data, timeline_value, view_type):
    return html.P('No data available', style={'color': '#6c757d', 'fontStyle': 'italic'})

# User Guide content callback
@callback(
    Output('userguide-content', 'children'),
    Input('userguide-tabs', 'value')
)
def update_userguide_content(tab):
    if tab == 'model-info':
        return html.Div([
            html.H4('SEATIRD Epidemic Model'),
            html.P('The pandemic simulator uses a SEATIRD compartmental model to simulate disease spread.'),
            html.Ul([
                html.Li(html.B('S - Susceptible: ') + 'Individuals who can become infected'),
                html.Li(html.B('E - Exposed: ') + 'Individuals who have been exposed but are not yet infectious'),
                html.Li(html.B('A - Asymptomatic: ') + 'Infectious individuals without symptoms'),
                html.Li(html.B('T - Treatable: ') + 'Symptomatic individuals who can receive treatment'),
                html.Li(html.B('I - Infected: ') + 'Symptomatic infectious individuals'),
                html.Li(html.B('R - Recovered: ') + 'Individuals who have recovered and are immune'),
                html.Li(html.B('D - Deceased: ') + 'Individuals who have died from the disease')
            ])
        ])
    else:
        return html.Div([
            html.H4('How to Use the Pandemic Simulator'),
            html.Ol([
                html.Li(html.B('Set Disease Parameters: ') + 'Configure the disease characteristics.'),
                html.Li(html.B('Select Initial Cases: ') + 'Choose which Texas counties will have initial cases.'),
                html.Li(html.B('Configure Interventions: ') + 'Set up interventions and treatments.'),
                html.Li(html.B('Run Simulation: ') + 'Click the Play button to start the simulation.'),
                html.Li(html.B('View Results: ') + 'Monitor the outbreak progression through visualizations.')
            ])
        ])

# Expose server for deployment
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)