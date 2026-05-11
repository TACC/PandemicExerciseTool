from dash import register_page, html

register_page(__name__)


def layout(**kwargs):
    return html.Div(html.H1('User Guide'))
