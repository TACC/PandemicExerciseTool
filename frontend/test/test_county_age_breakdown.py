"""Run from frontend: python -m pytest test/test_county_age_breakdown.py."""

from unittest.mock import Mock, patch

import dash
import pytest

import app  # noqa: F401 - Register pages before importing callbacks.
from county_data import county_metrics
from pages import home


def output_county():
    values = {'S': 100, 'E': 10, 'IA': 2, 'IP': 3, 'IS': 5, 'H': 7, 'R': 20, 'D': 1}
    return {
        'fips_id': '48201',
        'compartment_summary': {key: value * 60 for key, value in values.items()},
        'compartment_subgroups': {
            key: {
                risk: {vax: [value * (age + 1) for age in range(5)] for vax in ('U', 'V')}
                for risk in ('L', 'H')
            }
            for key, value in values.items()
        },
    }


def test_sums_risk_and_vaccination_counts_without_double_counting():
    county = county_metrics(output_county())
    assert county['ageGroups'][0]['infected'] == 40
    assert county['ageGroups'][0]['deceased'] == 4
    assert sum(age['infected'] for age in county['ageGroups']) == county['infected']
    assert sum(age['deceased'] for age in county['ageGroups']) == county['deceased']
    assert county['ageGroups'][0]['infectedPercent'] == pytest.approx(10 / 148 * 100, rel=0, abs=5e-8)
    assert county['ageGroups'][4]['deceasedPercent'] == pytest.approx(1 / 148 * 100, rel=0, abs=5e-8)

def test_legacy_models_and_zero_population():
    legacy_infectious = county_metrics({'compartment_summary': {
        'S': 80, 'A': 3, 'I': 4, 'T': 5, 'R': 8,
    }})
    assert legacy_infectious['infected'] == 12
    assert legacy_infectious['infectedPercent'] == 12
    county = output_county()
    for section in ('compartment_summary', 'compartment_subgroups'):
        county[section] = {key: val for key, val in county[section].items() if key in ('S', 'E', 'R')}
    legacy = county_metrics(county)
    assert legacy['deceased'] == 1200
    assert legacy['ageGroups'][0]['deceased'] == 80
    empty = county_metrics({
        'compartment_subgroups': {'S': {'L': {'U': [0] * 5}}},
    })
    assert empty['ageGroups'][0]['infectedPercent'] == 0
    assert empty['ageGroups'][0]['deceasedPercent'] == 0

def test_missing_and_incomplete_subgroups_are_unavailable():
    assert county_metrics({})['ageGroups'] is None
    county = output_county()
    county['compartment_subgroups']['S']['L']['U'] = [1, 2]
    assert county_metrics(county)['ageGroups'] is None


def test_fetch_retains_age_metrics():
    output = output_county()
    response = Mock(status_code=200, text='OK')
    response.json.return_value = {'day': 0, 'total_summary': output['compartment_summary'], 'data': [output]}
    with patch.object(home.requests, 'get', return_value=response):
        events, _, _, ages = home.fetch_simulation_data(1, {'isRunning': True}, [])
    day = events.to_plotly_json()['operations'][0]['params']['value']
    age_day = ages.to_plotly_json()['operations'][0]['params']['value']
    assert 'ageGroups' not in day['counties'][0]
    assert age_day['48201'][0]['infected'] == 40


def test_idle_poll_does_not_republish_history_or_trigger_rendering():
    events = [{'counties': []}]
    assert home.fetch_simulation_data(1, {'isRunning': False}, events) == (dash.no_update,) * 4
    response = Mock(status_code=404, text='not calculated')
    with patch.object(home.requests, 'get', return_value=response):
        assert home.fetch_simulation_data(1, {'isRunning': True}, events) == (dash.no_update,) * 4
