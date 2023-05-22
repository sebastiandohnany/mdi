import pandas as pd

import base64
import io
from dash import html, dcc, Input, Output, callback_context
import dash_bootstrap_components as dbc

from .server import app
from . import constants

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

# file upload parser
def parse_content(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    except Exception as e:
        return None

    return df

def country_filter_card():
    card_body = dbc.CardBody(
                            [
                                dbc.Row([
                                    dbc.Col([
                                        html.H6(
                                            "Start typing to select a country",
                                            className="card-text",
                                        )],
                                        className="col-9"
                                    ),
                                    dbc.Col([
                                        dbc.Button(
                                            className="fas fa-download",
                                            id="download_button",
                                            color="white",
                                            size="sm",

                                        ),
                                        dbc.Tooltip(
                                            f"Download a list of the selected countries",
                                            target=f"download_button",
                                            placement="top",
                                        ),

                                        dcc.Download(id="download")],
                                        className="col-1",
                                    ),
                                    dbc.Col([
                                        dcc.Upload(id="upload",
                                                   children=dbc.Button(
                                                       className="fas fa-upload",
                                                       id="upload_button",
                                                       color="white",
                                                       size="sm",
                                                   ),
                                                   style={
                                                       'margin': '0px',
                                                       'width': '1px'},
                                                   multiple=False
                                                   ),
                                        dbc.Tooltip(
                                            f"Upload a list of countries. "
                                            f"Must be a csv file containing a "
                                            f"'countries' column title followed by a "
                                            f"list of country codes in IOS Alpha‑3 format.",
                                            target=f"upload_button",
                                            placement="top",
                                        ),
                                    ],
                                        className="col-1",
                                    )

                                ]

                                ),
                                html.Div(
                                    dbc.Alert(
                                        id="upload-alert",
                                        is_open=False,
                                        duration=3000,
                                        style={"margin-top":"10px"}
                                    )
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
                                            style={
                                                "margin": "5px"
                                            },
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
                                            style={
                                                "margin": "5px"
                                            },
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
                                            style={
                                                "margin": "5px"
                                            },
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
                                            style={
                                                "margin": "5px"
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flex-direction": "row",
                                        "flex-wrap": "wrap",
                                    },
                                ),
                                html.Div([
                                    dcc.Dropdown(
                                        id="country-filter",
                                        options=dropdown_options,
                                        value=list(
                                            constants.country_regions.keys()
                                        ),
                                        multi=True,
                                        className="dcc_control",
                                    ),
                                ])

                            ]
                        )
    return card_body

@app.callback(
    Output("download", "data"),
    Input(component_id="download_button", component_property="n_clicks"),
    Input(component_id="country-filter", component_property="value"))
def generate_csv(n_nlicks, value):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if "download_button" in changed_id:
        #Put the list of countried into df and set it as index column
        df_selected_countries = pd.DataFrame(data={"countries": value})
        df_selected_countries.set_index('countries', inplace=True)

        return dcc.send_data_frame(df_selected_countries.to_csv, filename="country_list.csv")




