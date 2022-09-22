import pandas as pd
import numpy as np
import os

from dash import html, dcc, Input, Output, State, ctx

from .server import app

server = app.server
from . import constants, card_texts

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
    if country == "default":
        pass
    else:
        option_dictionary = {
            "label": html.Div(
                [
                    html.I(
                        className="fas fa-solid fa-circle fa-2xs",
                        style={
                            "color": constants.country_colors[country],
                            "margin-right": "5px",
                        },
                    ),
                    html.Div(
                        [constants.country_codes[country] + f" ({country})"],
                        style={"color": constants.country_colors[country]},
                        className="select-text",
                    ),
                ],
                style={
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                },
            ),
            "value": country,
            "search": constants.country_codes[country],
        }
        dropdown_options.append(option_dictionary)


# methodology file, modal, button
with open(ROOT + "assets/methodology.md", "r") as f:
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
                        html.A(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Img(
                                                id="logo",
                                                src=app.get_asset_url(
                                                    "NSA-RSA-logo-small.png"
                                                ),
                                                height="90px",
                                            ),
                                            md="auto",
                                            align="left",
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Row(
                                                    html.Div(
                                                        [
                                                            html.H2(
                                                                "Military Deployment Index"
                                                            ),
                                                        ],
                                                        id="app-title",
                                                    )
                                                ),
                                                dbc.Row(
                                                    html.Div(
                                                        [
                                                            html.H6(
                                                                "Measure and visualization of troop deployments"
                                                            ),
                                                        ],
                                                    )
                                                ),
                                            ],
                                            md=True,
                                            align="center",
                                        ),
                                    ],
                                    style={"background-color": "#fafafa"},
                                )
                            ],
                            href="https://ras-nsa.ca/",
                            style={
                                "color": "inherit",
                                "text-decoration": "none",
                            },
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
                    style={"margin-top": 20, "margin-bottom": 20},
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
                                html.H5(
                                    card_texts.mdi_extra_text,
                                    className="card-text mdi-text",
                                ),
                                style={
                                    "margin": "0.5rem 0.5rem 0.5rem 0.5rem",
                                    "background": "#FEBDB9",
                                    "height": "96%",
                                    "padding": "1rem 1rem 1rem 1rem",
                                },
                            )
                        ),
                        dbc.Col(
                            [
                                dbc.Card(id="card-mdi", style=constants.card_style),
                            ],
                            className="col-lg-8, col-md-8 col-12 col-sm-12",
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
                                                html.H6(
                                                    "Drag the slider to select a year",
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
                                                    included=False,
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
                                                html.H6(
                                                    "Start typing to select a country",
                                                    className="card-text",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                dbc.Button(
                                                                    "Select all",
                                                                    size="sm",
                                                                    outline=True,
                                                                    color="primary",
                                                                    id="country-all-button",
                                                                )
                                                            ],
                                                            style={"margin": "5px"},
                                                        ),
                                                        html.Div(
                                                            [
                                                                dbc.Button(
                                                                    "Deselect all",
                                                                    size="sm",
                                                                    outline=True,
                                                                    color="primary",
                                                                    id="country-none-button",
                                                                )
                                                            ],
                                                            style={"margin": "5px"},
                                                        ),
                                                        html.Div(
                                                            [
                                                                dbc.Button(
                                                                    "Select all NATO",
                                                                    size="sm",
                                                                    outline=True,
                                                                    color="primary",
                                                                    id="country-nato-button",
                                                                )
                                                            ],
                                                            style={"margin": "5px"},
                                                        ),
                                                        html.Div(
                                                            [
                                                                dbc.Button(
                                                                    "Select all EU",
                                                                    size="sm",
                                                                    outline=True,
                                                                    color="primary",
                                                                    id="country-eu-button",
                                                                )
                                                            ],
                                                            style={"margin": "5px"},
                                                        ),
                                                    ],
                                                    style={
                                                        "display": "flex",
                                                        "flex-direction": "row",
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="country-filter",
                                                    options=dropdown_options,
                                                    value=list(
                                                        constants.country_regions.keys()
                                                    ),
                                                    multi=True,
                                                    className="dcc_control",
                                                ),
                                            ]
                                        )
                                    ],
                                    style=constants.card_style,
                                ),
                            ],
                            className="col-lg-4 col-md-4 col-12 col-sm-12",
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        html.I(
                                            className="fas fa-regular fa-circle-info",
                                            id=f"target_map",
                                            style={
                                                "text-align": "right",
                                                "zIndex": "100",
                                                "position": "absolute",
                                                "top": "18px",
                                                "right": "16px",
                                                "margin": 0,
                                                "padding": 0,
                                            },
                                        ),
                                        dbc.Tooltip(
                                            card_texts.map_info_circle,
                                            target=f"target_map",
                                            style={
                                                "position": "absolute",
                                                "zIndex": "100",
                                            },
                                        ),
                                        dbc.Switch(
                                            id="military-presence-switch",
                                            label="Military presence",
                                            value=False,
                                            style={
                                                "zIndex": "100",
                                                "position": "absolute",
                                                "top": "18px",
                                                "left": "52px",
                                                "margin": 0,
                                                "padding": 0,
                                                "color": "#795548",
                                            },
                                        ),
                                        dcc.Graph(
                                            id="graph-map",
                                            config=dict(
                                                displaylogo=False,
                                                displayModeBar=False,
                                            ),
                                        ),
                                    ],
                                    style=constants.card_style,
                                )
                            ],
                            className="col-lg-8, col-md-8 col-12 col-sm-12",
                        ),
                    ],
                ),
                dbc.Row(
                    [dbc.Card(id="card-line", style={"background": "white"})],
                    style={"margin": "0.5rem 0.5rem 0.5rem 0.5rem"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    id="card-population", style=constants.card_style
                                )
                            ],
                            className="col-lg-4 col-md-4 col-12 col-sm-12",
                        ),
                        dbc.Col(
                            [
                                dbc.Card(id="card-active", style=constants.card_style),
                            ],
                            className="col-lg-4 col-md-4 col-12 col-sm-12",
                        ),
                        dbc.Col(
                            [dbc.Card(id="card-theatre", style=constants.card_style)],
                            className="col-lg-4 col-md-4 col-12 col-sm-12",
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    id="card-bar-orgs", style=constants.card_style
                                ),
                                dbc.Card(
                                    id="card-countries-orgs", style=constants.card_style
                                ),
                            ]
                        ),
                        dbc.Col(
                            dbc.Card(id="card-sunburst", style=constants.card_style),
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
        html.Footer(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    html.Pre(
                                        [
                                            "Network for Strategic Analysis (NSA)  |  "
                                            "Robert Sutherland Hall, Suite 403, Queen's University, 138 Union St  |  "
                                            "Kingston (Ontario)  K7L 3N6 Canada ",
                                            html.Br(),
                                        ]
                                    ),
                                ),
                                dbc.Row(
                                    [
                                        html.Pre(
                                            [
                                                html.I(className="fas fa-phone fa-xs"),
                                                " +1 613 533-2381  |  ",
                                                html.A(
                                                    [
                                                        html.I(
                                                            className="fas fa-envelope fa-xs"
                                                        ),
                                                        " info@ras-nsa.ca",
                                                    ],
                                                    href="mailto:info@ras-nsa.ca",
                                                    target="_blank",
                                                    style={
                                                        "color": "inherit",
                                                        "text-decoration": "none",
                                                        "font-family": "var(--bs-font-monospace)",
                                                    },
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                            ],
                            className="col-10",
                        ),
                        dbc.Col(
                            dbc.Row(
                                [
                                    html.Pre(
                                        [
                                            html.A(
                                                html.I(
                                                    className="fa-brands fa-facebook fa-xl"
                                                ),
                                                href="https://www.facebook.com/networkforstrategicanalysis/",
                                                target="_blank",
                                                style={"color": "inherit"},
                                            ),
                                            "  ",
                                            html.A(
                                                html.I(
                                                    className="fa-brands fa-linkedin fa-xl"
                                                ),
                                                href="https://www.linkedin.com/company/ras-nsa/",
                                                target="_blank",
                                                style={"color": "inherit"},
                                            ),
                                            "  ",
                                            html.A(
                                                html.I(
                                                    className="fa-brands fa-twitter fa-xl"
                                                ),
                                                href="https://twitter.com/RAS_NSA",
                                                target="_blank",
                                                style={"color": "inherit"},
                                            ),
                                            "  ",
                                            html.A(
                                                html.I(
                                                    className="fa-brands fa-youtube fa-xl"
                                                ),
                                                href="https://www.youtube.com/playlist?list=PLz41uVKaYyLT0m0MVtPn8W0l3aVJhTPPd",
                                                target="_blank",
                                                style={"color": "inherit"},
                                            ),
                                        ]
                                    )
                                ]
                            ),
                            style={"text-align": "right"},
                        ),
                    ],
                    style={
                        "margin-bottom": "2vh",
                    },
                ),
                dbc.Row(
                    html.Pre(
                        [
                            "Source code available from ",
                            html.A(
                                "GitHub",
                                href="https://github.com/sebastiandohnany/mdi",
                                target="_blank",
                                style={
                                    "color": "inherit",
                                    "font-family": "var(--bs-font-monospace)",
                                },
                            ),
                            ". |  Source of data: The International Institute of Strategic Studies.",
                        ]
                    )
                ),
                dbc.Row(
                    [
                        html.Pre(
                            "How to cite: RAS-NSA 2022. The Military Deployment Index. Available from: www.mdi.ras-nsa.can"
                        )
                    ]
                ),
                dbc.Row(
                    [
                        html.Pre(
                            [
                                "\u00A9",
                                " 2022 Barbora Tallová, Sebastián Dohnány, Natália Bajnoková",
                            ]
                        )
                    ]
                ),
            ],
            style={
                "margin": "2vw 0 0 0",
                "padding-top": "3vw",
                "padding-bottom": "1vw",
                "padding-left": "var(--bs-gutter-x, 1.4rem)",
                "padding-right": "var(--bs-gutter-x, 1.4rem)",
                "color": "gray",
                "background-color": "#fafafa",
                "fontSize": 15,
            },
        ),
    ],
    style={
        "background-color": "#fafafa",
        "padding": "0vw 3vw 0vw",
    },
)

from . import update_functions

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


@app.callback(
    Output(component_id="country-filter", component_property="value"),
    Input(component_id="country-all-button", component_property="n_clicks"),
    Input(component_id="country-none-button", component_property="n_clicks"),
    Input(component_id="country-nato-button", component_property="n_clicks"),
    Input(component_id="country-eu-button", component_property="n_clicks"),
    State(component_id="country-filter", component_property="value"),
)
def country_button_select(all_clicks, none_clicks, nato_clicks, un_clicks, value):

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "country-none-button":
        return ["USA"]

    elif button_id == "country-nato-button":
        return constants.nato_countries

    elif button_id == "country-eu-button":
        return constants.eu_countries

    else:
        return list(constants.country_regions.keys())
