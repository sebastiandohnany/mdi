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


def percentage_calculate(n, d, scaling=1):
    try:
        number = (n/d) * scaling
        return round(number, 1)
    except ZeroDivisionError:
        return 0


def format_number(number):
    if number>999:
        number = number/1000
        return str(round(number, 1)) + " K"
    else:
        return str(round(number, 1))


def horizontal_bar_plot(values, countries, bar_labels, max_value, percentage=False, condensed=False, colour="rgba(255, 0, 0, 0.8)"):
    fig = go.Figure(
        data=[go.Bar(y=countries, x=values, orientation="h", marker=dict(color=colour),
                     width=np.full(len(values), 0.2))],
        layout={
            "margin": {"pad": 20},
        }
    )

    fig.add_trace(go.Bar(y=countries, x=[max_value - value for value in values], orientation="h",
                         marker=dict(color="rgb(58, 59, 60)"), width=np.full(len(values), 0.2)))
    fig.update_traces(hoverinfo="skip")
    fig.update(layout_showlegend=False)
    fig.update_layout(paper_bgcolor="rgb(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", barmode="stack",
                      yaxis={"categoryorder":"array", "categoryarray":countries},
                      font=dict(
                          size=15),
                      height=120,
                      margin=dict(l=0, r=0, t=0, b=0)
                    )
    fig.update_xaxes(showticklabels=False, automargin=True, showgrid=False, visible=False)
    fig.update_yaxes(automargin=True, showgrid=False)
    if condensed:
        fig.update_layout(
            title_text="Top 5",
            font=dict(
                size=12,
            ),
            margin=dict(l=0, r=0, t=30, b=0)
        )
    annotations = []

    for value, country in zip(bar_labels, countries):
        value_str = str(value)
        if percentage:
            value_str = value_str + "%"

        annotations.append(dict(xref="x1", yref="y1",
                                y=country, x=max_value+0.08*max_value,
                                text=value_str,

                                showarrow=False))
    fig.update_layout(annotations=annotations)
    return fig


def meter_plot(indicator_value, absolute_value, range):
    fig = go.Figure(
        data=[go.Indicator(value=indicator_value,
                           mode="gauge+number",
                           gauge={"axis": {"visible": False, "range": [0, 100]},
                                  "bar": {"color": "rgba(255, 0, 0, 0.8)"},
                                  "bordercolor": "#fafafa",
                                  "steps": [
                                      {"range": [range["min"], indicator_value], "color": "rgba(255, 0, 0, 0.8)"},
                                      {"range": [indicator_value, range["max"]], "color": "rgb(58, 59, 60)"}]
                                  },
                           domain={"row": 0, "column": 100},
                           number={"suffix": "%", "font": {"size": 30}})]
    )

    fig.add_annotation(x=0.5, y=0.4,
                       text=f"{format_number(absolute_value)} troops",
                       font=dict(size=15),
                       showarrow=False
    )
    fig.update_layout(margin=dict(l=0, r=0, t=1, b=0),
                      height=120,
                      paper_bgcolor="rgb(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def country_orgs_bar_plot(df, condensed=False):
    fig = px.bar(df, x="Country", y="Deployed",
                 color="Organisation",
                 color_discrete_map={**constants.organisation_colors, **constants.country_colors},
                 custom_data= ["Organisation", "Percentage of Total Deployment"]
                 )

    fig.update_traces(hovertemplate="<b>Country: %{x}</b><br>"
                                    + "Organisation: %{customdata[0]} <br>"
                                    + "Deployed: %{y} <br>"
                                    + "Percentage Deployed: %{customdata[1]} % <br>")
    if condensed:
        fig.update_layout(
            title_text="Top 5",
            font=dict(
                size=12,
            ),
            margin=dict(l=0, r=0, t=30, b=0)
        )
    fig.update_layout(paper_bgcolor="rgb(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      legend=dict(bgcolor="rgba(0,0,0,0)")
                      )

    return fig


def summary_graph_card(title, text, card_info, graph, title_colour, extra_text=None):
    card = dbc.CardBody([
        dbc.Row([
            dbc.Col(
                html.H4(
                    title,
                    style={"color": title_colour, 'display': 'inline-block', 'margin-right': '5px'}),
            ),
            dbc.Col([
                html.I(className="fas fa-regular fa-circle-info", id="target", style={'text-align': 'right'}),
                dbc.Tooltip(card_info, target="target"),
            ], style={'text-align': 'right'})
        ]
        ),
        html.H6(
            text,
            className="card-text",
        ),
        dcc.Graph(figure=graph) if graph else "",
        html.P(extra_text) if extra_text else ""
    ])

    return card
