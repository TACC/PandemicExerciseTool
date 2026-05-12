from dash import register_page, html

register_page(__name__, title='About epiENGAGE')


def layout(**kwargs):
    return html.Div(html.H1('About Us'))
