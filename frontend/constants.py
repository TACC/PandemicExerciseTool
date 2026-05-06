# ============================================================================
# MODEL OPTIONS
# ============================================================================
MODEL_OPTIONS = [
    {
        'label': 'SEIRS Deterministic',
        'value': 'seirs-deterministic',
        'description': 'SEIR with waning immunity; Euler updates; fractional flows; stochastic binomial travel.',
    },
    {
        'label': 'SEIRS Stochastic',
        'value': 'seirs-stochastic',
        'description': 'SEIR with waning immunity; Poisson transitions; stochastic binomial travel.',
    },
    {
        'label': 'SEATIRD Deterministic',
        'value': 'seatird-deterministic',
        'description': 'Adds treatable compartment; Euler updates (fractional flows); stochastic binomial travel.',
    },
    {
        'label': 'SEATIRD Stochastic',
        'value': 'seatird-stochastic',
        'description': 'SEATIRD with exponential transitions (Gillespie, individual-level stochasticity); stochastic binomial travel.',
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
            'nu': [0.000022319, 0.000040975, 0.000083729, 0.000061809, 0.000008978],
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
            'nu': [0.05, 0.002, 0.01, 0.05, 0.15],
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
            'nu': [0.000022319, 0.000040975, 0.000083729, 0.000061809, 0.000008978],
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
            'nu': [0.05, 0.002, 0.01, 0.05, 0.15],
        },
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
        },
    },
}

VACCINE_MODELS = {
    'stockpile-age-risk': 'Stockpile Release by Age',  # Currently doesn't allow for risk preference
}

# ============================================================================
# OTHER OPTIONS
# ============================================================================

# Age group constants
AGE_GROUPS = [
    {'value': '0-4 years', 'label': '0-4 years'},
    {'value': '5-17 years', 'label': '5-17 years'},
    {'value': '18-49 years', 'label': '18-49 years'},
    {'value': '50-64 years', 'label': '50-64 years'},
    {'value': '65+ years', 'label': '65+ years'},
]

AGE_GROUP_MAPPING = {
    '0-4 years': '0',
    '5-17 years': '1',
    '18-49 years': '2',
    '50-64 years': '3',
    '65+ years': '4',
}
