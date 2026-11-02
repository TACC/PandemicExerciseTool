"""Community grid and detail panel checks; no browser or simulation required."""

import json
import pytest
from types import SimpleNamespace
from unittest.mock import patch

import dash
import dash_ag_grid as dag

import app
from county_data import county_metrics
from county_grid import age_panel, create_county_grid_panel, grid_columns, grid_rows
from pages import home
from test.test_county_age_breakdown import output_county
from test.test_disease_parameters import components


@pytest.fixture
def county():
    return county_metrics(output_county())


@pytest.fixture
def county_day(county):
    return {'day': 0, 'counties': [county], 'mapping': {'Harris': '48201'}}


@pytest.fixture
def age_request(county):
    return {'fips': '48201', 'day': 0, 'pending': False, 'ages': county['ageGroups']}


@pytest.fixture
def selected_rows():
    return [{'fips': '48201', 'name': 'Harris', 'infected': 600, 'outcome': 60}]


def test_layout_uses_community_grid_and_separate_detail_panel():
    panel = list(components(create_county_grid_panel()))
    grid = next(c for c in panel if isinstance(c, dag.AgGrid))
    assert not grid.enableEnterpriseModules
    assert grid.getRowId == 'params.data.fips'
    assert grid.dashGridOptions['rowSelection']['mode'] == 'singleRow'
    assert 'masterDetail' not in grid.dashGridOptions
    assert 'autoHeight' not in grid.dashGridOptions
    ids = [getattr(c, 'id', None) for c in panel]
    assert 'county-age-body' in ids
    assert 'expanded-counties' not in ids
    assert not any(isinstance(value, dict) for value in ids)


def test_grid_rows_use_numeric_values_and_exclude_age_history(county_day, selected_rows):
    assert grid_rows(county_day, 'count') == selected_rows
    percent = grid_rows(county_day, 'percent')[0]
    assert percent['infected'] == pytest.approx(10 / 148 * 100, rel=0, abs=5e-8)
    assert percent['outcome'] == pytest.approx(1 / 148 * 100, rel=0, abs=5e-8)
    assert 'ageGroups' not in percent
    zero_padded = grid_rows(
        {'counties': [{'fips': '1001'}], 'mapping': {'Autauga': '01001'}}, 'count'
    )[0]
    assert zero_padded['fips'] == '01001'
    assert zero_padded['name'] == 'Autauga'


def test_empty_data_and_model_headers():
    rows, columns, style = home.update_county_grid(None, 'count', 'seirs-deterministic')
    assert rows == []
    assert style == {'display': 'none'}
    assert columns[2]['headerName'] == 'Recovered'
    assert grid_columns('percent', 'seihrd-stochastic')[2]['headerName'] == 'Deceased'
    assert 'sort' not in columns[1]
    assert columns[1]['initialSort'] == 'desc'


def test_selection_links_to_map_and_clears_on_jurisdiction_change(selected_rows):
    with patch.object(home, 'ctx', SimpleNamespace(triggered_id='county-grid')):
        assert home.select_grid_county(selected_rows, 'Texas', None) == '48201'
        assert home.select_grid_county(selected_rows, 'Texas', '48201') is dash.no_update
        assert home.select_grid_county([], 'Texas', '48201') is None
    with patch.object(home, 'ctx', SimpleNamespace(triggered_id='selected-state-store')):
        assert home.select_grid_county(selected_rows, 'Delaware', '48201') is None
    assert home.clear_grid_selection('Delaware') == []


def test_detail_panel_has_five_age_groups_and_follows_count_percentage_mode(
    age_request, selected_rows
):
    for view, expected in [
        ('count', ['0-4 years', '40', '4']),
        ('percent', ['0-4 years', '6.8%', '0.7%']),
    ]:
        title, body = age_panel('48201', age_request, view, 'seihrd-stochastic', selected_rows)
        assert title == 'Harris — age breakdown'
        table = body.children[-1]
        rows = table.children[1].children
        assert len(rows) == 5
        assert [cell.children for cell in rows[0].children] == expected
        assert table.children[0].children.children[2].children == 'Deceased'
    _, body = age_panel('48201', age_request, 'count', 'seirs-stochastic', selected_rows)
    assert body.children[-1].children[0].children.children[2].children == 'Recovered'


def test_details_handle_no_selection_pending_unavailable_and_stale_county(
    age_request, selected_rows
):
    _, body = age_panel(None, age_request, 'count', '', [])
    assert 'Select a county' in body.children
    for request in (None, {**age_request, 'pending': True}, {**age_request, 'fips': '48001'}):
        _, body = age_panel('48201', request, 'count', '', selected_rows)
        assert 'Loading' in body.children
    _, body = age_panel('48201', {**age_request, 'ages': None}, 'count', '', selected_rows)
    assert 'unavailable' in body.children


def call_callback(output_token, values, changed):
    client = app.app.server.test_client()
    assert client.get('/_dash-layout').status_code == 200
    key = next(key for key in app.app.callback_map if output_token in key)
    callback = app.app.callback_map[key]
    outputs = callback['output']
    output_list = outputs if isinstance(outputs, list) else [outputs]
    output_spec = [
        {'id': out.component_id, 'property': out.component_property} for out in output_list
    ]
    response = client.post(
        '/_dash-update-component',
        json={
            'output': key,
            'outputs': output_spec if isinstance(outputs, list) else output_spec[0],
            'inputs': [{**item, 'value': values[item['id']]} for item in callback['inputs']],
            'state': [{**item, 'value': values[item['id']]} for item in callback['state']],
            'changedPropIds': [changed],
        },
    )
    assert response.status_code == 200, response.data
    return response.get_json()['response']


def test_registered_callbacks_process_254_counties_then_one_selected_detail(
    county, county_day, age_request, selected_rows
):
    counties = [{**county, 'fips': str(48001 + i * 2)} for i in range(254)]
    response = call_callback(
        'county-grid.rowData',
        {
            'county-table-day': {**county_day, 'counties': counties},
            'view-toggle': 'count',
            'selected-model-store': 'seihrd-stochastic',
        },
        'county-table-day.data',
    )
    assert len(response['county-grid']['rowData']) == 254
    assert 'ageGroups' not in json.dumps(response)
    selection = call_callback(
        'selected-county-store.data',
        {
            'county-grid': selected_rows,
            'selected-state-store': 'Texas',
            'selected-county-store': None,
        },
        'county-grid.selectedRows',
    )
    assert selection['selected-county-store']['data'] == '48201'
    response = call_callback(
        'county-age-title.children',
        {
            'selected-county-store': '48201',
            'county-selected-age': age_request,
            'view-toggle': 'percent',
            'selected-model-store': 'seihrd-stochastic',
            'county-grid': selected_rows,
        },
        'county-selected-age.data',
    )
    assert response['county-age-title']['children'] == 'Harris — age breakdown'
    assert '6.8%' in json.dumps(response)
    assert 'county-grid' not in response


def test_legacy_expansion_is_not_registered():
    client = app.app.server.test_client()
    deps = client.get('/_dash-dependencies').get_json()
    assert not any('expanded-counties' in item['output'] for item in deps)
    assert not any('county-age-collapse' in item['output'] for item in deps)
    assert not any('spread-table.children' in item['output'] for item in deps)
