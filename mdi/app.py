import pandas as pd
import numpy as np
import os

from dash import html, dcc, Input, Output, State

from .server import app

server = app.server
from . import constants

import dash_bootstrap_components as dbc
import plotly.io as pio

from dotenv import load_dotenv

load_dotenv()
ROOT = os.getenv("PROJECT_ROOT")

pio.templates.default = "plotly_white"
from dash_bootstrap_templates import load_figure_template

load_figure_template("litera")

# data
df = pd.read_excel(ROOT + "data/MDVA_Deployments_LatLon.xlsx")
mapbox_access_token = open(ROOT + ".mapbox_token").read()

# country colors
df["Color"] = df["Country"].replace(to_replace=constants.country_colors)

# deployments and presence
df_deployments = df[df["MissionType"] == "Operation"]
df_presence = df[df["MissionType"] == "MillitaryPresence"]


# navbar
with open(ROOT + "static/methodology.md", "r") as f:
    howto_md = f.read()

modal_overlay = dbc.Modal(
    [
        dbc.ModalBody(html.Div([dcc.Markdown(howto_md)], id="howto-md")),
        dbc.ModalFooter(dbc.Button("Close", id="howto-close", className="howto-bn")),
    ],
    id="modal",
    size="lg",
)

button_howto = dbc.Button(
    "Methodology",
    id="howto-open",
    outline=True,
    color="info",
    # Turn off lowercase transformation for class .button in stylesheet
    style={"textTransform": "none"},
)

button_github = dbc.Button(
    "Source",
    outline=True,
    color="primary",
    href="https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-image-segmentation",
    id="gh-link",
    style={"text-transform": "none"},
)

# layout
app.layout = html.Div(
    [
        html.Header(
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Img(
                                        id="logo",
                                        src=app.get_asset_url(
                                            "../static/NSA-RSA-logo-small.png"
                                        ),
                                        height="70px",
                                    ),
                                    md="auto",
                                    align="left",
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H3("Millitary Deployments Index"),
                                            ],
                                            id="app-title",
                                        )
                                    ],
                                    md=True,
                                    align="center",
                                ),
                            ],
                            # align="center",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.NavbarToggler(id="navbar-toggler"),
                                        dbc.Collapse(
                                            dbc.Nav(
                                                [
                                                    dbc.NavItem(button_howto),
                                                ],
                                                navbar=True,
                                            ),
                                            id="navbar-collapse",
                                            navbar=True,
                                        ),
                                        modal_overlay,
                                    ],
                                    md=2,
                                ),
                            ],
                            align="right",
                        ),
                    ],
                    fluid=True,
                ),
                dark=False,
                color="white",
                sticky="top",
            )
        ),
        dbc.Container(
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="graph-map",
                                                    config={"displaylogo": False},
                                                ),
                                            ],
                                        )
                                    ],
                                    style=constants.card_style,
                                ),
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.P(
                                                    "Choose a year",
                                                    className="card-text",
                                                ),
                                                dcc.Slider(
                                                    id="year-slider",
                                                    min=df["Year"].min(),
                                                    max=df["Year"].max(),
                                                    step=None,
                                                    value=df["Year"].max(),
                                                    marks={
                                                        str(year): str(year)
                                                        for year in df["Year"].unique()
                                                    },
                                                ),
                                            ]
                                        )
                                    ],
                                    style=constants.card_style,
                                ),
                            ],
                            md=7,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    id="card-sunburst", style=constants.card_style
                                ),
                                dbc.Card(id="card-line", style=constants.card_style),
                            ]
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(id="card-active", style=constants.card_style),
                        ),
                        dbc.Col(
                            dbc.Card(id="card-population", style=constants.card_style),
                        ),
                        dbc.Col(
                            [dbc.Card(id="card-theatre", style=constants.card_style)]
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(id="card-bar-orgs", style=constants.card_style),
                            md=4,
                        ),
                        dbc.Col(
                            dbc.Card(
                                id="card-countries-orgs", style=constants.card_style
                            ),
                            md=8,
                        ),
                    ]
                ),
                dcc.Store(id="selected-countries"),
                dcc.Store(id="selected-year"),
            ],
            # style={"fontFamily": constants.theme["fontFamily"]},
            fluid=True,
        ),
        html.Footer(),
    ]
)

import mdi.countries

# Callback for modal popup
@app.callback(
    Output("modal", "is_open"),
    [Input("howto-open", "n_clicks"), Input("howto-close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# we use a callback to toggle the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
