from dash import register_page, html, dcc

register_page(__name__, title='About epiENGAGE')


def layout(**kwargs):
    return html.Div(
        [
            html.H1('About Us'),
            html.P("The epiENGAGE Interactive Outbreak Simulator is a pandemic and epidemic simulation application that models epidemics within all 50 US states + DC."),
            html.P('This project is funded by the NIH under the name "Interactive Outbreak Simulator: A Robust and Customizable Platform for Socio-Epidemiological Insights" (Project #1R03MD021096).'),
            html.P(
                html.Span([
                    "The Interactive Outbreak Simulator website was created by and is maintained by the ",
                    html.A("Texas Advanced Computing Center", href="https://tacc.utexas.edu/"),
                    " with support from ",
                    html.A("SGX3 ", href="https://sciencegateways.org"),
                    "(NSF award #2231406), an initiative of the Science Gateways Community Institute (NSF award #1547611)."
                ])
            ),
            html.Div(
                [
                    html.Img(src="./assets/NIH_logo.png"),
                    html.Img(src="./assets/TACC-primary-Black-.png"),
                    html.Img(src="./assets/sg-logos.png"),
                    html.Img(src="./assets/NSF_logo.png"),
                ],
                className="about-us__logo-div"
            ),
        ],
        style=({'padding': '20px', 'maxWidth': '800px', 'margin': '0 auto'})
    )
