"""Run from frontend: python -m pytest test/test_disease_parameters.py."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import dash
import pytest

import app  # noqa: F401 - Register Dash pages before importing their callbacks.
from constants import AGE_GROUPS, MODEL_OPTIONS, SEIHRD_DEFAULTS
from pages import home


def components(component):
    yield component
    children = getattr(component, 'children', None)
    if children is not None:
        for child in children if isinstance(children, (list, tuple)) else [children]:
            yield from components(child)


def make_inputs(model='seihrd-stochastic', preset=None):
    modal = home.update_disease_param_modal_body(model, preset, True)
    return {
        component.id['param']: component
        for component in components(modal)
        if isinstance(getattr(component, 'id', None), dict) and component.id['type'] == 'dp-input'
    }


def save_parameters(inputs, model='seihrd-stochastic'):
    states = [{'id': component.id} for component in inputs.values()]
    with patch.object(home, 'ctx', SimpleNamespace(states_list=[states])):
        return home.save_disease_parameters(
            1, [component.value for component in inputs.values()], [], model
        )[0]


def test_model_option_and_modal_defaults():
    assert 'seihrd-stochastic' in [option['value'] for option in MODEL_OPTIONS]
    assert 'seihrd-deterministic' not in [option['value'] for option in MODEL_OPTIONS]
    inputs = make_inputs()
    assert 'latent-period' not in inputs
    for param, default in SEIHRD_DEFAULTS.items():
        if isinstance(default, list):
            assert len(default) == len(AGE_GROUPS)
            assert [inputs[f'{param}-{i}'].value for i in range(len(default))] == default
        else:
            assert inputs[param].value == default
    assert inputs['E_to_IPandIA_days'].min > 0
    assert inputs['prop_E_to_IA-0'].max == 1
    assert home.update_disease_param_modal_body('seihrd-stochastic', {}, False) is dash.no_update


def test_empty_catalog():
    modal = home.update_disease_param_modal_body('seihrd-stochastic', {}, True)
    catalog = next(
        c
        for c in components(modal)
        if getattr(c, 'id', None)
        == {
            'type': 'dp-dropdown',
            'param': 'preset',
        }
    )
    assert catalog.options == []
    assert catalog.disabled


def test_save_custom_values_and_zero_proportions():
    preset = {
        param: [8.5 if param.endswith('_days') else 0] * len(default)
        if isinstance(default, list)
        else 8.5
        for param, default in SEIHRD_DEFAULTS.items()
    }
    preset.update(R0=0, disease_name='Custom SEIHRD', rel_inf_IA_to_IS=0)
    saved = save_parameters(make_inputs(preset=preset))
    for param in SEIHRD_DEFAULTS:
        assert saved[param] == preset[param]
    assert saved['R0'] == 0
    assert saved['scenario_name'] == 'Custom SEIHRD'


def test_blank_fields_use_defaults():
    inputs = make_inputs()
    inputs['IP_to_IS_days'].value = None
    inputs['H_to_R_days-0'].value = None
    inputs['prop_H_to_D-0'].value = 0
    saved = save_parameters(inputs)
    assert saved['IP_to_IS_days'] == SEIHRD_DEFAULTS['IP_to_IS_days']
    assert saved['H_to_R_days'][0] == SEIHRD_DEFAULTS['H_to_R_days'][0]
    assert saved['prop_H_to_D'][0] == 0


def test_payload_contains_saved_seihrd_fields():
    inputs = make_inputs()
    inputs['H_to_R_days-0'].value = 9.25
    inputs['prop_H_to_D-0'].value = 0
    saved = save_parameters(inputs)
    created = Mock(status_code=201, text='created')
    created.json.return_value = {'id': 1}
    started = Mock(status_code=202, text='started')
    started.json.return_value = {'task_id': 'test-task'}
    with (
        patch.object(home.requests, 'post', return_value=created) as post,
        patch.object(home.requests, 'get', return_value=started),
    ):
        result = home.toggle_simulation(
            1,
            {},
            saved,
            [],
            [],
            {},
            {},
            [],
            False,
            False,
            'seihrd-stochastic',
            'Illinois',
        )
    assert result[0]['isRunning']
    payload = post.call_args.kwargs['json']
    for param, default in SEIHRD_DEFAULTS.items():
        value = payload[param]
        if isinstance(default, list):
            value = [float(x) for x in value.split(',')] if param == 'sigma' else json.loads(value)
        assert value == saved[param]


@pytest.mark.parametrize(
    'model',
    [
        'seaitrd-deterministic',
        'seaitrd-stochastic',
        'seirs-deterministic',
        'seirs-stochastic',
    ],
)
def test_existing_models_keep_their_fields(model):
    inputs = make_inputs(model)
    assert 'latent-period' in inputs
    assert 'E_to_IPandIA_days' not in inputs
    saved = save_parameters(inputs, model)
    assert saved['model_type'] == model
    assert 'prop_H_to_D' not in saved


def test_seihrd_summary_shows_saved_parameters_and_initial_cases():
    inputs = make_inputs(preset={'disease_name': 'SEIHRD scenario', 'R0': 2.8})
    inputs['E_to_IPandIA_days'].value = 1.5
    inputs['H_to_R_days-0'].value = 9.25
    inputs['prop_H_to_D-0'].value = 0
    inputs['rel_inf_IA_to_IS'].value = 0
    saved = save_parameters(inputs)
    display = home.create_scenario_display(
        saved,
        [
            {
                'cases': 10,
                'age_group': '18-49 years',
                'location': 'Cook County',
            }
        ],
    )
    text = ' '.join(str(c) for c in components(display) if isinstance(c, (str, int, float)))
    assert 'Disease Parameters' in text
    assert 'Scenario:  SEIHRD scenario' in text
    assert 'Reproduction Number:  2.8' in text
    assert 'Latent Period:  1.5 days' in text
    assert 'Relative Asymptomatic Infectiousness:  0' in text
    lists = [c for c in components(display) if isinstance(c, home.html.Ul)]
    assert len(lists) == 6  # Five age-specific parameters and initial cases.
    assert [li.children for li in lists[0].children] == [
        '0-4 years: 9.25 days',
        '5-17 years: 4.8 days',
        '18-49 years: 6.2 days',
        '50-64 years: 6.8 days',
        '65+ years: 6.55 days',
    ]
    assert lists[3].children[0].children == '0-4 years: 0'
    assert 'Initial Cases' in text
    assert '10 aged 18-49 years in Cook County' in text


def test_seihrd_summary_without_initial_cases():
    display = home.create_scenario_display(save_parameters(make_inputs()), [])
    text = ' '.join(c for c in components(display) if isinstance(c, str))
    assert 'Disease Parameters' in text
    assert 'Hospital Admission to Recovery:' in text
    assert 'No scenario set yet.' not in text
    assert 'Initial Cases' not in text
