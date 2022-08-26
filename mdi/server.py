from dash import Dash

import dash_bootstrap_components as dbc

app = Dash(
    "Military Deployments Index",
    title="Military Deployments Index",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
