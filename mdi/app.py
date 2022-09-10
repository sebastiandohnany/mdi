import pandas as pd
import numpy as np
import os

from dash import html, dcc, Input, Output, State

from .server import app

server = app.server
from . import constants

import dash_bootstrap_components as dbc

# import plotly.io as pio

from dotenv import load_dotenv

load_dotenv()
ROOT = os.getenv("PROJECT_ROOT")


# Default plot theme
# import plotly.graph_objects as go


# pio.templates["mdi_plots"] = go.layout.Template(
#     layout_annotations=[
#         dict(
#             font=dict(family="Open Sans"),
#         )
#     ]
# )
# pio.templates.default = "plotly_white+mdi_plots"


from dash_bootstrap_templates import load_figure_template

load_figure_template("litera")

# data
df = pd.read_excel(ROOT + "data/MDVA_Deployments_LatLon.xlsx")
mapbox_access_token = open(ROOT + ".mapbox_token").read()

# country colors
df["Color"] = df["Country"].replace(to_replace=constants.country_colors)

# deployments and presence
df_deployments = df[df["MissionType"] == "Operation"]
df_presence = df[df["MissionType"] == "MilitaryPresence"]

dropdown_options = []
for country in list(constants.country_regions.keys()):
    if country == 'default':
        pass
    else:
        option_dictionary = {"label": html.Div([html.I(className="fas fa-solid fa-circle fa-2xs",
                                                       style={"color":constants.country_colors[country],
                                                              "margin-right":"5px"}),
                                               html.Div([constants.country_codes[country] + f" ({country})"],
                                                        style={"color": constants.country_colors[country] })]
                                               , style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                             "value": country,
                             "search":constants.country_codes[country]}
        dropdown_options.append(option_dictionary)



# methodology file, modal, button
with open(ROOT + "static/methodology.md", "r") as f:
    methodology_md = f.read()

modal_overlay = dbc.Modal(
    [
        dbc.ModalBody(html.Div([dcc.Markdown(methodology_md)], id="methodology-md")),
        dbc.ModalFooter(
            dbc.Button("Close", id="methodology-close", className="methodology-bn")
        ),
    ],
    id="modal",
    size="lg",
)

button_methodology = dbc.Button(
    "Methodology",
    id="methodology-open",
    outline=True,
    color="primary",
    # Turn off lowercase transformation for class .button in stylesheet
    style={"textTransform": "none"},
)

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
                                        src=app.get_asset_url("NSA-RSA-logo-small.png"),
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
                            style={"background-color": "#fafafa"},
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Nav(
                                            [
                                                dbc.NavItem(button_methodology),
                                            ],
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
                sticky="top",
                style={"background-color": "#fafafa"},
            ),
            style={"background-color": "#fafafa"},
        ),
        dbc.Container(
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                id="card-mdi",
                                style={
                                    "margin": "0.5rem 0.5rem 0.5rem 0.5rem",
                                    "background": "#FEBDB9",
                                },
                            )
                        ),
                        dbc.Col(
                            dbc.Card(id="card-theatre", style=constants.card_style)
                        ),
                        dbc.Col(
                            dbc.Card(id="card-bar-orgs", style=constants.card_style)
                        ),
                    ]
                ),
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
                                )
                            ], className="col-7"
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardBody(
                                            [
                                                html.H6(
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
                                            ],
                                        )
                                    ],
                                    style=constants.card_style,
                                ),
                                dbc.Card(
                                    [
                                        dbc.CardBody([
                                            html.H6("Choose countries", className="card-text"),
                                            dcc.Dropdown(
                                                id="country-filter",
                                                options=dropdown_options,
                                                value=list(constants.country_regions.keys()),
                                                multi=True,
                                                className="dcc_control",
                                            ),
                                        ], style=constants.card_style)
                                ]),
                            ],
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(id="card-line", style=constants.card_style),
                            ], className="col-8"
                        ),
                        dbc.Col(
                            [
                                dbc.Card(id="card-active", style=constants.card_style),
                                dbc.Card(id="card-population", style=constants.card_style),
                            ]
                        ),
                    ],
                    className="g-0",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(id="card-sunburst", style=constants.card_style),
                        ),
                        dbc.Col(
                            dbc.Card(
                                id="card-countries-orgs", style=constants.card_style
                            )
                        ),
                    ]
                ),
                dcc.Store(id="selected-countries"),
                dcc.Store(id="selected-year"),
            ],
            style={"background-color": "#fafafa"},
            # style={"fontFamily": constants.theme["fontFamily"]},
            fluid=True,
        ),
        html.Footer(),
    ]
)

from . import countries

# methodology modal popup
@app.callback(
    Output("modal", "is_open"),
    [Input("methodology-open", "n_clicks"), Input("methodology-close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
