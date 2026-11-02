"""Frontend unit tests; no running backend required.

Run from frontend: python -m pytest test/test_app_unit.py
"""


def test_data_loading():
    """County data produces matching dropdown options."""
    from test.data_loader import DataLoader

    loader = DataLoader()
    counties = loader.load_texas_counties()
    assert counties, 'Expected at least one county'
    assert all({'name', 'fips', 'population'} <= county.keys() for county in counties)

    options = loader.get_county_dropdown_options()
    assert options == [{'label': county['name'], 'value': county['fips']} for county in counties]


def test_visualization():
    """The current Dash renderers handle an empty simulation."""
    import app  # noqa: F401 - Register Dash pages before importing their callbacks.
    from pages import home

    empty_map = home._create_empty_map()
    assert not empty_map.data
    assert empty_map.layout.height == 400

    empty_chart = home._build_chart_figure([], 0, 'seirs-deterministic')
    assert not empty_chart.data
    assert empty_chart.layout.title.text == 'Epidemic Curve - No Data Available'

    rows, columns, controls = home.update_county_grid(None, 'percent', 'seirs-deterministic')
    assert rows == []
    assert columns[2]['headerName'] == 'Recovered'
    assert controls == {'display': 'none'}
