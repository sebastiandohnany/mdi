import pandas as pd
import numpy as np
from collections import Counter

from dash import Input, Output, State, exceptions
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State

from .server import app
from . import constants

graph_config = dict(displaylogo=False, displayModeBar=False)


def percentage_calculate(n, d, scaling=1):
    try:
        number = (n / d) * scaling
        return round(number, 1)
    except ZeroDivisionError:
        return 0


def format_number(number):
    if number > 999:
        number = number / 1000
        return "{:,}K".format(round(number, 1))
    else:
        return str(round(number, 1))


def horizontal_bar_plot(
    values,
    countries,
    bar_labels,
    max_value,
    percentage=False,
    condensed=False,
    colour="rgba(255, 0, 0, 0.8)",
):
    fig = go.Figure(
        data=[
            go.Bar(
                y=countries,
                x=values,
                orientation="h",
                marker=dict(color=colour),
                width=np.full(len(values), 0.2),
            )
        ],
        layout={
            "margin": {"pad": 20},
        },
    )

    fig.add_trace(
        go.Bar(
            y=countries,
            x=[max_value - value for value in values],
            orientation="h",
            marker=dict(color="#D4D4D4"),
            width=np.full(len(values), 0.2),
        )
    )
    fig.update_traces(hoverinfo="skip")
    fig.update(layout_showlegend=False)
    fig.update_layout(
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="stack",
        yaxis={"categoryorder": "array", "categoryarray": countries},
        font=dict(size=15),
        height=120,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.update_xaxes(
        showticklabels=False, automargin=True, showgrid=False, visible=False
    )
    fig.update_yaxes(automargin=True, showgrid=False)
    annotations = []

    for value, country in zip(bar_labels, countries):
        value_str = str(value)
        if percentage:
            value_str = value_str + "%"

        annotations.append(
            dict(
                xref="x1",
                yref="y1",
                y=country,
                x=max_value + 0.08 * max_value,
                text=value_str,
                showarrow=False,
            )
        )
    fig.update_layout(annotations=annotations)
    return fig


def meter_plot(
    indicator_value, absolute_value, range, bar_colour="rgba(255, 0, 0, 0.8)"
):
    fig = go.Figure(
        data=[
            go.Indicator(
                value=indicator_value,
                mode="gauge+number",
                gauge={
                    "axis": {"visible": False, "range": [0, 100]},
                    "bar": {"color": bar_colour},
                    "bordercolor": "#fafafa",
                    "steps": [
                        {"range": [range["min"], indicator_value], "color": bar_colour},
                        {"range": [indicator_value, range["max"]], "color": "#D4D4D4"},
                    ],
                },
                domain={"row": 0, "column": 100},
                number={"suffix": "%", "font": {"size": 30}},
            )
        ]
    )

    fig.add_annotation(
        x=0.5,
        y=0.4,
        text=f"{format_number(absolute_value)} TROOPS",
        font=dict(size=15),
        showarrow=False,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=1, b=0),
        height=120,
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def country_orgs_bar_plot(df, condensed=False):

    if len(df["Country"].unique()) == 1:
        fig = px.bar(
            df,
            x="Deployed",
            y="Organisation",
            color="Organisation",
            color_discrete_map={
                **constants.organisation_colors,
                **constants.country_colors,
            },
            custom_data=["Organisation", "Percentage of Total Deployment"],
            orientation="h",
        )
    else:
        fig = px.bar(
            df,
            x="Country",
            y="Deployed",
            color="Organisation",
            color_discrete_map={
                **constants.organisation_colors,
                **constants.country_colors,
            },
            custom_data=["Organisation", "Percentage of Total Deployment"],
        )

    fig.update_traces(
        hovertemplate="<b>Country: %{x}</b><br>"
        + "Organisation: %{customdata[0]} <br>"
        + "Deployed: %{y} <br>"
        + "Percentage Deployed: %{customdata[1]} % <br>"
    )
    if condensed:
        fig.update_layout(
            title_text="Top 5",
            font=dict(
                size=12,
            ),
            margin=dict(l=0, r=0, t=30, b=0),
        )
    fig.update_layout(
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=250,
    )

    return fig


def summary_graph_card(
    title,
    text,
    card_info,
    graph,
    title_colour=constants.colors["title"],
    extra_text=None,
):
    info_circle = ""
    if card_info is not None:
        info_circle = dbc.Col(
            [
                html.I(
                    className="fas fa-regular fa-circle-info",
                    id=f"target_{title}",
                    style={"text-align": "right"},
                ),
                dbc.Tooltip(card_info, target=f"target_{title}"),
            ],
            style={"text-align": "right"},
        )

    card = dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H4(
                            title,
                            style={
                                "color": title_colour,
                                "display": "inline-block",
                                "margin-right": "5px",
                            },
                        ),
                    ),
                    info_circle,
                ]
            ),
            html.H6(
                text,
                className="card-text",
            ),
            dcc.Graph(figure=graph, config=graph_config) if graph else "",
            html.P(extra_text) if extra_text else "",
        ]
    )

    return card


def comparison_summary_graph_card(side_1, side_2, card_info):
    card = dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4(
                                side_1["Title"],
                                style={
                                    "color": side_1["Title colour"],
                                    "display": "inline-block",
                                    "margin-right": "5px",
                                },
                            ),
                        ],
                        className="col-6",
                    ),
                    dbc.Col(
                        [
                            html.H4(
                                side_2["Title"],
                                style={
                                    "color": side_2["Title colour"],
                                    "display": "inline-block",
                                    "margin-right": "5px",
                                },
                            )
                        ],
                        className="col-5",
                    ),
                    dbc.Col(
                        [
                            html.I(
                                className="fas fa-regular fa-circle-info",
                                id="target",
                                style={"text-align": "right"},
                            ),
                            dbc.Tooltip(card_info, target="target"),
                        ],
                        className="col-1",
                        style={"text-align": "right"},
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H6(
                                side_1["Text"],
                                className="card-text",
                            ),
                            dcc.Graph(figure=side_1["Graph"], config=graph_config)
                            if side_1["Graph"]
                            else "",
                        ],
                        className="col-6",
                    ),
                    dbc.Col(
                        [
                            html.H6(
                                side_2["Text"],
                                className="card-text",
                            ),
                            dcc.Graph(figure=side_2["Graph"], config=graph_config)
                            if side_2["Graph"]
                            else "",
                        ],
                        className="col-6",
                    ),
                ]
            ),
        ]
    )

    return card
