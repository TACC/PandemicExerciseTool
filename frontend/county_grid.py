"""AG Grid Community county table and selected-county age details."""

import math

from dash import dcc, html
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

from constants import AGE_GROUPS


def outcome_label(model):
    return 'Recovered' if (model or '').lower().startswith('seir') else 'Deceased'


def grid_columns(view='count', model='seirs-deterministic'):
    formatter = (
        "d3.format(',.1f')(params.value) + '%'" if view == 'percent'
        else "d3.format(',d')(Math.floor(params.value))"
    )
    numeric = {
        # Align values only: numericColumn also reverses the header icon order.
        'cellClass': 'ag-right-aligned-cell', 'filter': 'agNumberColumnFilter',
        'valueFormatter': {'function': formatter},
        'getQuickFilterText': {'function': formatter},
        'flex': 1, 'minWidth': 95,
    }
    return [
        {'field': 'name', 'headerName': 'County', 'filter': 'agTextColumnFilter',
         'flex': 1.3, 'minWidth': 120},
        {**numeric, 'field': 'infected', 'headerName': 'Infectious', 'initialSort': 'desc'},
        {**numeric, 'field': 'outcome', 'headerName': outcome_label(model)},
    ]


def create_county_grid_panel():
    return html.Div(
        html.Div([
            html.H6('County Data', className='mb-2 county-table__title'),
            html.Div([
                # Optional cross-column search; column filters remain available.
                # dbc.Input(id='county-search', type='text',
                #           placeholder='Search (county name or value)…', debounce=True,
                #           class_name='mb-2'),
                dbc.RadioItems(id='view-toggle', options=[
                    {'label': ' Percentage', 'value': 'percent'},
                    {'label': ' Count', 'value': 'count'},
                ], value='count', inline=True, label_class_name='view-toggle__label',
                    class_name='mb-3 ps-2'),
            ], id='county-controls', style={'display': 'none'}),
            dcc.Store(id='county-table-day', data=None),
            dcc.Store(id='county-selected-age', data=None),
            html.Div([
                dag.AgGrid(
                    id='county-grid', columnDefs=grid_columns(), rowData=[], selectedRows=[],
                    getRowId='params.data.fips', enableEnterpriseModules=False,
                    defaultColDef={'sortable': True, 'resizable': True, 'editable': False,
                                   'wrapHeaderText': False, 'autoHeaderHeight': True},
                    dashGridOptions={
                        'rowSelection': {'mode': 'singleRow', 'enableClickSelection': True,
                                         'checkboxes': False},
                        'animateRows': False, 'rowHeight': 34,
                        'overlayNoRowsTemplate': 'No county data available.',
                    },
                    columnSize='responsiveSizeToFit',
                    style={'height': '100%', 'minHeight': 0, 'width': '100%', 'flex': '1 1 0'},
                ),
                html.Section([
                    html.H6('Age breakdown', id='county-age-title', className='mb-2'),
                    dcc.Loading(html.Div(
                        html.P('Select a county to view its age breakdown.', className='m-0 text-muted'),
                        id='county-age-body', **{'aria-live': 'polite'},
                    ), type='dot', delay_show=250, show_initially=False),
                ], className='county-grid-details', **{'aria-labelledby': 'county-age-title'}),
            ], className='county-grid-content'),
        ], className='sim-layout__right'),
        className='sim-layout__col--right',
    )


def grid_rows(day, view):
    day = day or {}
    names = {str(fips).zfill(5): name for name, fips in day.get('mapping', {}).items()
             if name.lower() != 'all'}
    infected = 'infectedPercent' if view == 'percent' else 'infected'
    outcome = 'deceasedPercent' if view == 'percent' else 'deceased'
    return [
        {'fips': str(county['fips']).strip().zfill(5),
         'name': names.get(str(county['fips']).strip().zfill(5), str(county['fips']).zfill(5)),
         'infected': float(county.get(infected) or 0),
         'outcome': float(county.get(outcome) or 0)}
        for county in day.get('counties', []) if county.get('fips')
    ]


def age_panel(selected, request, view, model, selected_rows):
    if not selected:
        return 'Age breakdown', html.P('Select a county to view its age breakdown.', className='m-0 text-muted')
    name = next((row['name'] for row in (selected_rows or []) if row.get('fips') == selected), selected)
    title = f'{name} — age breakdown'
    if not request or request.get('fips') != selected or request.get('pending'):
        return title, html.P('Loading age breakdown…', role='status', className='m-0 text-muted')
    ages = request.get('ages')
    if not ages or len(ages) != len(AGE_GROUPS):
        return title, html.P('Age breakdown unavailable for this output.', className='m-0 text-muted')

    def display(age, count, percent):
        return f'{age[percent]:.1f}%' if view == 'percent' else f'{math.floor(age[count]):,}'

    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th('Age group', scope='col'),
            html.Th('Infectious', scope='col', className='text-end'),
            html.Th(outcome_label(model), scope='col', className='text-end'),
        ])),
        html.Tbody([
            html.Tr([
                html.Th(group['label'], scope='row'),
                html.Td(display(age, 'infected', 'infectedPercent'), className='text-end'),
                html.Td(display(age, 'deceased', 'deceasedPercent'), className='text-end'),
            ]) for group, age in zip(AGE_GROUPS, ages)
        ]),
    ], size='sm', striped=True, className='county-age-table mb-0')
    children = []
    if view == 'percent':
        children.append(html.P('Percentage of each age group’s county population.',
                               className='small text-muted mb-2'))
    return title, html.Div([*children, table])
