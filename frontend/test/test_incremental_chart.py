"""Exercise chart patches against the complete figure without a browser."""

import copy
import json
import pytest

from dash import Patch

import app
from pages import home
from test.test_disease_parameters import components


def day(index):
    return {
        'day': index,
        'totalSusceptible': 1000 - index,
        'totalExposed': index * 2,
        'totalAsymptomaticCount': index * 3,
        'totalTreatableCount': index * 4,
        'totalInfectedCount': index * 5,
        'totalRecoveredCount': index * 6,
        'totalDeceased': index * 7,
    }


def frame(count, start=0, timeline=None, model='seirs-deterministic'):
    return {
        'start': start,
        'count': count,
        'model': model,
        'day': timeline,
        'points': [day(index) for index in range(start, count)],
    }


def apply_patch(figure, patch):
    result = copy.deepcopy(figure.to_plotly_json())
    for operation in patch.to_plotly_json()['operations']:
        destination = result
        for part in operation['location'][:-1]:
            destination = destination[part]
        key = operation['location'][-1]
        value = operation['params']['value']
        if operation['operation'] == 'Extend':
            destination[key] = list(destination[key]) + value
        else:
            assert operation['operation'] == 'Assign'
            destination[key] = value
    return result


def test_chart_stores_mount_with_home_page_not_global_shell():
    global_ids = {
        getattr(component, 'id', None)
        for component in components(app.app.layout)
        if isinstance(getattr(component, 'id', None), str)
    }
    home_ids = {
        getattr(component, 'id', None)
        for component in components(home.create_home_layout())
        if isinstance(getattr(component, 'id', None), str)
    }
    for component_id in ('chart-frame', 'chart-progress', 'line-chart', 'timeline-slider'):
        assert component_id not in global_ids
        assert component_id in home_ids


@pytest.mark.parametrize(
    'model',
    [
        'seirs-deterministic',
        'seihrd-stochastic',
        'seaitrd-deterministic',
    ],
)
def test_initialization_and_batched_append_match_complete_figure(model):
    initial, *_, progress = home.update_chart(frame(2, timeline=1, model=model))
    assert progress == {'count': 2, 'model': model}
    patch, *_, progress = home.update_chart(frame(5, start=2, timeline=4, model=model))
    assert isinstance(patch, Patch)
    updated = apply_patch(initial, patch)
    expected = home._build_chart_figure([day(i) for i in range(5)], 4, model)
    assert updated['data'] == expected.to_plotly_json()['data']
    assert updated['layout'] == expected.to_plotly_json()['layout']
    assert progress['count'] == 5


def test_scrubbing_only_moves_marker_and_does_not_duplicate_points():
    initial = home.update_chart(frame(5, timeline=4))[0]
    for selected in (0, 2, 2, 4, None):
        patch = home.update_chart(frame(5, start=5, timeline=selected))[0]
        operations = patch.to_plotly_json()['operations']
        assert all(op['location'][0] == 'layout' for op in operations)
        updated = apply_patch(initial, patch)
        assert updated['data'] == initial.to_plotly_json()['data']
        assert updated['layout']['shapes'][0]['visible'] is (selected is not None)
        assert updated['layout']['shapes'][0]['x0'] == (selected or 0)


def test_reset_and_model_change_rebuild():
    for empty_frame in (None, frame(0)):
        figure, style, _, _, progress = home.update_chart(empty_frame)
        assert not figure.data
        assert style == {'display': 'none'}
        assert progress is None
    rebuilt = home.update_chart(frame(1, timeline=0, model='seihrd-stochastic'))[0]
    assert not isinstance(rebuilt, Patch)
    assert len(rebuilt.data) == 7
    assert list(rebuilt.data[0].x) == [0]


def test_marker_uses_actual_day_and_can_start_hidden():
    request = frame(1)
    request['points'][0]['day'] = 10
    initial = home.update_chart(request)[0]
    assert not initial.layout.shapes[0].visible
    request = frame(1, start=1, timeline=10)
    updated = apply_patch(initial, home.update_chart(request)[0])
    assert updated['layout']['shapes'][0]['x0'] == 10
    assert updated['layout']['annotations'][0]['text'] == 'Day 10'


def test_http_callback_accepts_only_small_frame_and_returns_patch():
    client = app.app.server.test_client()
    assert client.get('/_dash-layout').status_code == 200
    key = next(key for key in app.app.callback_map if 'line-chart.figure' in key)
    callback = app.app.callback_map[key]
    assert [item['id'] for item in callback['inputs']] == ['chart-frame']
    assert not callback['state']
    request = frame(300, start=300, timeline=100)
    response = client.post(
        '/_dash-update-component',
        json={
            'output': key,
            'outputs': [
                {'id': output.component_id, 'property': output.component_property}
                for output in callback['output']
            ],
            'inputs': [{'id': 'chart-frame', 'property': 'data', 'value': request}],
            'state': [],
            'changedPropIds': ['chart-frame.data'],
        },
    )
    assert response.status_code == 200
    output = response.get_json()['response']['line-chart']['figure']
    assert '__dash_patch_update' in output
    assert all(op['location'][0] == 'layout' for op in output['operations'])
    assert len(json.dumps(request)) < 150
