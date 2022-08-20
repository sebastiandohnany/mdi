import pandas as pd
import numpy as np

from dash import html, dcc

from mdi.server import app
import mdi.constants as constants

# data
df = pd.read_excel("./data/MDVA_Deployments_LatLon.xlsx")
mapbox_access_token = open(".mapbox_token").read()

# country colors
df["Color"] = df["Country"].replace(to_replace=constants.country_colors)

# deployments and presence
df_deployments = df[df["MissionType"] == "Operation"]
df_presence = df[df["MissionType"] == "MillitaryPresence"]

# layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(
                        id="graph-map",
                        config={"displaylogo": False},
                    ),
                ),
                dcc.Slider(
                    id="year-slider",
                    min=df["Year"].min(),
                    max=df["Year"].max(),
                    step=None,
                    value=df["Year"].max(),
                    marks={str(year): str(year) for year in df["Year"].unique()},
                ),
                dcc.Store(id="selected-countries"),
                dcc.Store(id="selected-year"),
            ],
        ),
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(
                        id="graph-line",
                    )
                ),
                html.Div(
                    dcc.Graph(
                        id="graph-sunburst",
                    )
                ),
            ],
        ),
    ],
    style={"fontFamily": constants.theme["fontFamily"]},
)

import mdi.countries
