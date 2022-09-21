from dash import Dash

import dash_bootstrap_components as dbc

app = Dash(
    "Military Deployment Index",
    title="Military Deployment Index",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
)
