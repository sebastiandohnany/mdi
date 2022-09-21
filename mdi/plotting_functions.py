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
    if d == 0:
        return 0
    else:
        number = (n / d) * scaling
        return round(number, 1)


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
    colour=constants.colors["title"],
):
    bar_width_ration = 0.5

    if len(countries) == 1:
        bar_width_ration = 0.2

    fig = go.Figure(
        data=[
            go.Bar(
                y=countries,
                x=values,
                orientation="h",
                marker=dict(color=colour),
                width=np.full(len(values), bar_width_ration),
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
            width=np.full(len(values), bar_width_ration),
        )
    )
    fig.update_traces(hoverinfo="skip")
    fig.update(layout_showlegend=False)
    fig.update_layout(
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="stack",
        yaxis={"categoryorder": "array", "categoryarray": countries},
        font=dict(size=constants.theme["titlefont_size"]),
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
                    xshift=15,
                )
            )
        else:
            annotations.append(
                dict(
                    xref="x1",
                    yref="y1",
                    y=country,
                    x=max_value + 0.08 * max_value,
                    text=value_str,
                    showarrow=False,
                    xshift=10,
                )
            )
    fig.update_layout(annotations=annotations)
    return fig


def meter_plot(
    indicator_value, absolute_value, range, bar_colour=constants.colors["title"]
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
        x=0.49,
        y=0.45,
        text="{:,}".format(absolute_value),
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
    df.rename(columns={"Organisation": "Command"}, inplace=True)
    if len(df["Country"].unique()) == 1:
        fig = px.bar(
            df,
            x="Deployed",
            y="Command",
            color="Command",
            color_discrete_map={
                **constants.organisation_colors,
                **constants.country_colors,
            },
            custom_data=["Command", "Percentage of Total Deployment"],
            orientation="h",
        )
        fig.update_layout(
            yaxis_title=None,
            xaxis_tickformat=",",
        )
        fig.update_traces(
            hovertemplate="<b>Command: %{customdata[0]}</b><br>"
            + "Deployed: %{x:,} <br>"
            + "Share: %{customdata[1]:.2}% <br>"
            + "<extra></extra>"
        )

    else:
        fig = px.bar(
            df,
            x="Country",
            y="Deployed",
            color="Command",
            color_discrete_map={
                **constants.organisation_colors,
                **constants.country_colors,
            },
            custom_data=["Command", "Percentage of Total Deployment"],
        )
        fig.update_layout(
            margin=dict(l=100, r=0, t=0, b=0),
            xaxis_title=None,
            yaxis_tickformat=",",
            yaxis_title_standoff=60,
        )
        fig.update_traces(
            hovertemplate="<b>Country: %{x}</b><br>"
            + "<b>Command: %{customdata[0]}</b><br>"
            + "Deployed: %{y:,} <br>"
            + "Share: %{customdata[1]:.2}% <br>"
            + "<extra></extra>"
        )

    if condensed:
        fig.update_layout(
            title_text="Top 5",
            font=dict(
                size=12,
            ),
            margin=dict(l=0, r=0, t=30, b=0),
        )
    fig.update_xaxes(
        title_standoff=constants.theme["title_standoff"],
        tickfont_size=constants.theme["tickfont_size"],
        titlefont_size=constants.theme["titlefont_size"],
        ticksuffix="    ",
    )
    fig.update_yaxes(
        title_standoff=constants.theme["title_standoff"],
        tickfont_size=constants.theme["tickfont_size"],
        titlefont_size=constants.theme["titlefont_size"],
        ticksuffix="     ",
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
    modal_id=None,
    full_graph=None,
    title_colour=constants.colors["title"],
):
    expand_button = ""
    modal_overlay= ""
    if full_graph is not None:
        modal_overlay = modal_overlay_template(modal_id, full_graph)
        expand_button = html.I(
            className="fas fa-plus-square",
            id=f"expand_{modal_id}",
            style={"text-align": "right", "margin-right":"10px"},
        )

        # Population expand graph
        @app.callback(
            Output(f"full-{modal_id}-graph", "is_open"),
            [Input(f"expand_{modal_id}", "n_clicks"),
             Input(f"expand-{modal_id}-close", "n_clicks")],
            [State(f"full-{modal_id}-graph", "is_open")],
        )
        def toggle_modal(n1, n2, is_open):
            if n1 or n2:
                return not is_open
            return is_open

    info_circle = ""
    if card_info is not None:
        info_circle = dbc.Col(
            [
                expand_button,
                html.I(
                    className="fa-regular fa-circle-info",
                    id=f"target_{title}",
                    style={"text-align": "right"},
                ),
                dbc.Tooltip(card_info, target=f"target_{title}"),
                modal_overlay,
            ],
            style={"text-align": "right"},
        )

    card = dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H1(
                            str(title).upper(),
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
        ]
    )

    return card


def summary_graph_card_small(
    title,
    text,
    card_info,
    graph,
    title_colour=constants.colors["title"],
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
                            str(title),
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
        ]
    )

    return card


def plot_graph_card(
    title,
    text,
    card_info,
    graph,
    title_colour=constants.colors["cardName"],
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
                        html.H5(
                            str(title).capitalize(),
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
                                side_1["Text"].upper(),
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
                                side_2["Text"].upper(),
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

def modal_overlay_template(id, graph):
    modal = dbc.Modal(
        [
            dbc.ModalBody(dcc.Graph(figure=graph), id=f"expand-{id}-md"),
            dbc.ModalFooter(
                dbc.Button("Close", id=f"expand-{id}-close")
            ),
        ],
        id=f"full-{id}-graph",
        size="xl",

    )

    return modal