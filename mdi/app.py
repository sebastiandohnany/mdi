import os

import pandas as pd
from dotenv import load_dotenv

from dash import html, dcc, Input, Output, State, ctx, callback_context
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

from .server import app
from . import constants, card_texts
from .country_filter import country_filter_card, parse_content

server = app.server

load_dotenv()
ROOT = os.getenv("PROJECT_ROOT")


load_figure_template("litera")

# data
df = pd.read_excel(ROOT + "data/MDVA_Deployments_LatLon.xlsx")
mapbox_access_token = open(ROOT + ".mapbox_token").read()

# country colors
df["Color"] = df["Country"].replace(to_replace=constants.country_colors)

# deployments and presence
df_deployments = df[df["MissionType"] == "Operation"]
df_presence = df[df["MissionType"] == "MilitaryPresence"]

#Year slider marks dictionary, this is necessary for disabling labels for odd years
year_slider_marks = {}
for year in df["Year"].unique():
    if year % 2 == 0:
        year_slider_marks[str(year)] = str(year)
    else:
        year_slider_marks[str(year)] = ""

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
                            [dbc.Card(
                                html.H5(
                                    card_texts.mdi_extra_text,
                                    className="card-text mdi-text",
                                ),
                                style=constants.mdi_col_style,
                            )], style=constants.row_style
                        ),
                        dbc.Col(
                            [
                                dbc.Card(id="card-mdi", style=constants.card_style),
                            ],
                            className="col-lg-8, col-md-8 col-sm-12",
                            style=constants.row_style
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
                                                    min=df[
                                                            "Year"
                                                        ].min(),
                                                    max=df[
                                                            "Year"
                                                    ].max(),
                                                    step=None,
                                                    value=df[
                                                        "Year"
                                                    ].max(),
                                                    marks=year_slider_marks,
                                                    tooltip={"placement":"top", "always_visible": True},
                                                    included=False,
                                                ),
                                            ],
                                        )
                                    ],
                                    style=constants.card_style,
                                ),
                            ]
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    [
                                                        country_filter_card()
                                                    ],
                                                    style=constants.map_col_style,
                                                ),
                                            ]
                                        )
                                    ]
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
                                    style=constants.map_col_style,
                                )
                            ],
                            className="col-lg-8, col-md-8 col-12 col-sm-12",
                        ),
                    ], style=constants.row_style
                ),
                dbc.Row(
                    [
                        dbc.Card(id="card-line", style={"background": "white"})
                    ],
                    style={"margin": "0.5rem 0.5rem 0.5rem 0.5rem"},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    id="card-population", style=constants.card_style,
                                )
                            ], style=constants.row_style,
                            className="col-lg-4 col-md-12 col-12 col-sm-12",
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    id="card-active", style=constants.card_style,
                                ),
                            ], style=constants.row_style,
                            className="col-lg-4 col-md-12 col-12 col-sm-12",
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    id="card-theatre", style=constants.card_style
                                )
                            ], style=constants.row_style,
                            className="col-lg-4 col-md-12 col-12 col-sm-12",
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    id="card-bar-orgs",
                                                    style=constants.card_style,
                                                )
                                            ]
                                        )
                                    ], style=constants.row_style
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Card(
                                                    id="card-countries-orgs",
                                                    style=constants.card_style,
                                                )
                                            ]
                                        )
                                    ], style=constants.row_style
                                ),
                            ],
                        ),
                        dbc.Col([
                            dbc.Card(id="card-sunburst", style=constants.card_style),
                        ], style=constants.row_style
                        ),
                    ],
                ),
                dcc.Store(id="selected-countries"),
                dcc.Store(id="selected-year"),
            ],
            style={"background-color": "#fafafa"},
            fluid=True,
        ),
        html.Footer(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                        [
                                            "Network for Strategic Analysis (NSA)  |  "
                                            "Robert Sutherland Hall, Suite 403, Queen's University, 138 Union St  |  "
                                            "Kingston (Ontario)  K7L 3N6 Canada",
                                            html.Br(),
                                        ]
                                    ),
                                html.Div(
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
                                    ],
                                    style={
                                        "margin-top": "0.5vh",
                                    }
                                ),
                            ],
                            className="col-lg-10 col-md-10 col-12 col-sm-12",
                        ),
                        dbc.Col(
                            [
                                html.Div(
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
                            ],
                            style={"text-align": "right",
                                   "margin-bottom": "1vh"
                                   },
                        ),
                    ],
                    style={
                        "margin-bottom": "2vh",
                    },
                ),
                dbc.Row(
                    [
                        html.Div(
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
                    ],
                    style={
                        "margin-bottom": "2vh",
                    }
                ),
                dbc.Row(
                    [
                        html.Div(
                            "Suggested citation: Massie, J., Tallová, B., Dohnány, S., Bajnoková, N., (2022) Military Deployment Index. Network for Strategic Analysis. Available at: http://www.mdi.ras-nsa.ca/."
                        )
                    ],
                    style={
                        "margin-bottom": "2vh",
                    }
                ),
                dbc.Row(
                    [
                        html.Div(
                            [
                                "\u00A9",
                                " 2022 Barbora Tallová, Sebastián Dohnány, Natália Bajnoková",
                            ]
                        )
                    ],
                    style={
                        "margin-bottom": "2vh",
                        "margin-top": "2vh",
                    }
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
                "fontSize": 13,
                'letter-spacing': '.05rem',
                'word-spacing': '0.3rem',
            },
        ),
    ],
    style={
        "background-color": "#fafafa",
        "padding": "0vw 3vw 0vw",
    },
)

from . import update_functions
from . import country_filter

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

#####
# Unfortunately have None, None for each return as there is a bug inside the dcc.Upload so it's not allowing you to
# re-upload the same file (would have to refresh the page), workaround is to set the content of Upload to None
#####
@app.callback(
    Output(component_id="country-filter", component_property="value"),
    Output(component_id='upload', component_property='contents'),
    Output(component_id='upload', component_property='filename'),
    Output(component_id="upload-alert", component_property="children"),
    Output(component_id="upload-alert", component_property="is_open"),
    Output(component_id="upload-alert", component_property="color"),
    Input(component_id="country-all-button", component_property="n_clicks"),
    Input(component_id="country-none-button", component_property="n_clicks"),
    Input(component_id="country-nato-button", component_property="n_clicks"),
    Input(component_id="country-eu-button", component_property="n_clicks"),
    Input(component_id="upload", component_property="contents"),
    Input(component_id='upload', component_property='filename'),
    State(component_id="country-filter", component_property="value"),
)
def country_button_select(all_clicks, none_clicks, nato_clicks, un_clicks, contents, filename, value):
    """
    :return: country_list, upload_filename=None (because of the bug), upload_contents=None (because of the bug),
             upload_alert_message ("" if no alert), upload_alert_open (False if no alert), upload_alert_color ("" if no alert)
    """

    if not ctx.triggered:
        button_id = "No clicks yet"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    upload_filename = None
    upload_contents = None
    #Set arbitrary message, as long as upload_alert_open=False
    upload_alert_message = "Couldn't upload the file"
    upload_alert_open = False
    upload_alert_colour = "danger"

    if button_id == "country-none-button":
        return ["CAN"], upload_filename, upload_filename, upload_alert_message, upload_alert_open, upload_alert_colour

    elif button_id == "country-nato-button":
        return constants.nato_countries, upload_filename, upload_filename, upload_alert_message, upload_alert_open, \
               upload_alert_colour

    elif button_id == "country-eu-button":
        return constants.eu_countries, upload_filename, upload_filename, upload_alert_message, upload_alert_open, \
               upload_alert_colour

    elif button_id == "upload":
        if contents is not None:
            df = parse_content(contents, filename)

            if df is not None:
                country_list = df["countries"]

                wrong_codes = list(set(country_list).difference(constants.country_regions.keys()))

                #Filter out any countries with wrong format
                country_list = list(set(country_list).intersection(constants.country_regions.keys()))

                if wrong_codes:
                    upload_alert_message = f"The following country codes are invalid: {wrong_codes}"
                    upload_alert_open = True

                    return country_list, upload_filename, upload_contents, upload_alert_message , upload_alert_open, \
                           upload_alert_colour
                else:
                    upload_alert_message = "Successfully uploaded the country list"
                    upload_alert_open = True
                    upload_alert_colour = "success"
                    return country_list, upload_filename, upload_contents, upload_alert_message , upload_alert_open, \
                           upload_alert_colour

            else:
                upload_alert_open = True
                return [], upload_filename, upload_contents, upload_alert_message, upload_alert_open, \
                       upload_alert_colour
        else:
            upload_alert_open = True
            return [], upload_filename, upload_contents, upload_alert_message, upload_alert_open, \
                   upload_alert_colour

    else:
        return list(constants.country_regions.keys()), upload_filename, upload_contents, upload_alert_message, \
               upload_alert_open, upload_alert_colour


if __name__ == '__main__':
    app.run_server()
