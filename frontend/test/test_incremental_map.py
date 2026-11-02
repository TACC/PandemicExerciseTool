"""Run from frontend: python -m pytest test/test_incremental_map.py."""

import copy
import json

import dash
import pytest
from plotly.utils import PlotlyJSONEncoder

import app  # noqa: F401
from pages import home

pytestmark = pytest.mark.filterwarnings('error::DeprecationWarning')


def geometry():
    return {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'properties': {'GEOID': fips, 'NAME': name},
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [
                        [
                            [-100 + index, 30],
                            [-99 + index, 30],
                            [-99 + index, 31],
                            [-100 + index, 30],
                        ]
                    ],
                },
            }
            for index, (fips, name) in enumerate([('48001', 'Anderson'), ('48003', 'Andrews')])
        ],
    }


def apply_patch(figure, patch):
    result = copy.deepcopy(figure.to_plotly_json())
    for operation in patch.to_plotly_json()['operations']:
        assert operation['operation'] == 'Assign'
        destination = result
        for part in operation['location'][:-1]:
            destination = destination[part]
        destination[operation['location'][-1]] = operation['params']['value']
    return result


@pytest.fixture
def geojson():
    return geometry()


@pytest.fixture
def initialized_map(geojson):
    return home.initialize_incremental_map({'geojson': geojson}, 'Texas')


@pytest.fixture
def map_figure(initialized_map):
    return initialized_map[0]


@pytest.fixture
def map_metadata(initialized_map):
    return initialized_map[4]


def make_frame(view='count'):
    return {
        'state': 'Texas',
        'day': 7,
        'view': view,
        'values': [10, 20] if view == 'count' else [1, 2],
        'customdata': [['Anderson', 10, 1, 0], ['Andrews', 20, 2, 1]],
        'highlight': {'lon': [], 'lat': []},
    }


def test_initial_map_has_fixed_locations_and_reserved_highlight(map_figure, map_metadata):
    assert map_metadata['fips'] == ['48001', '48003']
    assert map_figure.layout.uirevision == 'Texas'
    assert len(map_figure.data) == 2
    assert list(map_figure.data[1].lon) == []
    assert [trace.type for trace in map_figure.data] == ['choroplethmap', 'scattermap']
    layout = map_figure.to_plotly_json()['layout']
    assert 'mapbox' not in layout
    assert layout['map']['style'] == 'white-bg'
    center, zoom = home._compute_mapbox_viewport(map_figure.data[0].geojson)
    assert layout['map']['center'] == center
    assert layout['map']['zoom'] == zoom


@pytest.mark.parametrize('view', ['count', 'percent'])
def test_count_and_percentage_patches_match_legacy_map(geojson, map_figure, map_metadata, view):
    counties = [
        {'fips': '48001', 'infected': 10, 'infectedPercent': 1, 'deceased': 0},
        {'fips': '48003', 'infected': 20, 'infectedPercent': 2, 'deceased': 1},
    ]
    patch, title = home.update_map_incrementally(make_frame(view), map_metadata)
    updated = apply_patch(map_figure, patch)
    old = home._create_jurisdiction_choropleth(
        [{'counties': counties}],
        0,
        view,
        geojson,
        'seihrd-stochastic',
        'Texas',
    ).to_plotly_json()
    for key in ('z', 'zmax', 'colorbar', 'customdata'):
        assert updated['data'][0][key] == old['data'][0][key]
    assert title == 'Epidemic Simulation (Day 7)'
    assert updated['layout'] == map_figure.to_plotly_json()['layout']
    assert updated['data'][0]['geojson'] == geojson


def test_selection_is_patched_and_cleared_without_touching_viewport(
    geojson, map_figure, map_metadata
):
    frame = make_frame()
    lon, lat = home._county_boundary_lines(geojson, '48001')
    frame['highlight'] = {'lon': lon, 'lat': lat}
    patch, _ = home.update_map_incrementally(frame, map_metadata)
    updated = apply_patch(map_figure, patch)
    assert updated['data'][1]['lon'] == lon
    clear, _ = home.update_map_incrementally(make_frame(), map_metadata)
    cleared = apply_patch(map_figure, clear)
    assert cleared['data'][1]['lon'] == []
    assert not any(op['location'][0] == 'layout' for op in patch.to_plotly_json()['operations'])


def test_missing_assets_and_state_switch(geojson):
    figure, style, _, _, metadata = home.initialize_incremental_map({}, 'Texas')
    assert not figure.data
    assert style == {'display': 'none'}
    assert metadata is None
    patch, _ = home.update_map_incrementally(make_frame(), {'state': 'Delaware'})
    assert patch is dash.no_update
    _, _, _, _, metadata = home.initialize_incremental_map(
        {'geojson': geojson, 'jurisdiction': 'Texas'},
        'Delaware',
    )
    assert metadata['state'] == 'Texas'


def test_patch_payload_excludes_boundaries_and_viewport(map_metadata):
    patch, _ = home.update_map_incrementally(make_frame(), map_metadata)
    payload = json.dumps(patch, cls=PlotlyJSONEncoder)
    assert 'geojson' not in payload
    assert 'mapbox' not in payload
    assert 'locations' not in payload
    assert all(op['location'][0] == 'data' for op in patch.to_plotly_json()['operations'])


def test_full_map_selection_uses_separate_line_without_changing_fill(geojson):
    plain = home._create_empty_state_map(geojson, selected_state='Texas')
    selected = home._create_empty_state_map(
        geojson,
        selected_state='Texas',
        selected_county='48001',
    )
    assert selected.data[0].to_plotly_json() == plain.data[0].to_plotly_json()
    outline = selected.data[1]
    assert outline.type == 'scattermap'
    assert outline.mode == 'lines'
    assert outline.line.width == 3
    assert outline.line.color == '#000000'
    assert outline.hoverinfo == 'skip'
    lon, lat = home._county_boundary_lines(geojson, '48001')
    assert list(outline.lon) == lon
    assert list(outline.lat) == lat
    assert selected.layout == plain.layout


def test_registered_callback_never_receives_history_or_full_figure(map_metadata):
    client = app.app.server.test_client()
    assert client.get('/_dash-layout').status_code == 200
    key = next(
        key
        for key, callback in app.app.callback_map.items()
        if any(item['id'] == 'map-frame' for item in callback['inputs'])
    )
    callback = app.app.callback_map[key]
    assert [item['id'] for item in callback['inputs']] == ['map-frame']
    assert [item['id'] for item in callback['state']] == ['map-metadata']
    response = client.post(
        '/_dash-update-component',
        json={
            'output': key,
            'outputs': [
                {'id': 'spread-map', 'property': 'figure'},
                {'id': 'epidemic-progress-title', 'property': 'children'},
            ],
            'inputs': [{'id': 'map-frame', 'property': 'data', 'value': make_frame()}],
            'state': [{'id': 'map-metadata', 'property': 'data', 'value': map_metadata}],
            'changedPropIds': ['map-frame.data'],
        },
    )
    assert response.status_code == 200, response.data
    assert b'__dash_patch_update' in response.data
    assert b'geojson' not in response.data
