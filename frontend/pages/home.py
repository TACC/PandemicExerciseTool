from dash import register_page, html

register_page(__name__, path='/')


def layout(**kwargs):
    return html.Div(html.H1('epiEngage'))
