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

#General function for percentage calculations scaling=100 gives % and scaling=100 give fractions
def percentage_calculate(n, d, scaling=1):
    if d == 0:
        return 0
    else:
        number = (n / d) * scaling
        return round(number, 1)

#Number formatting so that e.g. 10000=10,000
def format_number(number):
    if number > 999:
        number = number / 1000
        return "{:,}K".format(round(number, 1))
    else:
        return str(round(number, 1))

#Figrue with "floating" bars
def horizontal_bar_plot(
    values,
    countries,
    bar_labels,
    max_value,
    percentage=False,
    colour=constants.colors["title"],
):

    #Width of floating bar, less countries = thicker bar
    if len(countries) == 1:
        bar_width_ration = 0.2
    elif len(countries) == 2:
        bar_width_ration = 0.4
    else:
        bar_width_ration = 0.5

    #Make the plot
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

    #Make the bard
    fig.add_trace(
        go.Bar(
            y=countries,
            x=[max_value - value for value in values],
            orientation="h",
            marker=dict(color="#D4D4D4"),
            width=np.full(len(values), bar_width_ration),
        )
    )
    #Remove hover and legend
    fig.update_traces(hoverinfo="skip")
    fig.update(layout_showlegend=False)

    #Remove background colour and all axes
    fig.update_layout(
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        barmode="stack",
        yaxis={"categoryorder": "array", "categoryarray": countries},
        font=dict(size=constants.theme["titlefont_size"]),
        height=650,
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.update_xaxes(
        showticklabels=False, automargin=True, showgrid=False, visible=False
    )
    fig.update_yaxes(automargin=True, showgrid=False)
    annotations = []

    #Add country and value annotation to each side of the bar
    for value, country in zip(bar_labels, countries):
        if percentage:
            value_str = str(value) + "%"
        else:
            value_str = str(value) + " "

        annotations.append(
            dict(
                xref="x1",
                yref="y1",
                y=country,
                x=max_value + 0.03 * max_value,
                text=value_str,
                showarrow=False,
                xshift=15,
            )
        )
    fig.update_layout(annotations=annotations)
    return fig

#Meter plot
def meter_plot(
    indicator_value, absolute_value, range, bar_colour=constants.colors["title"]
):
    #Set the meter range and styling
    gauge = {
        "axis": {"visible": False, "range": [0, 100]},
        "bar": {"color": bar_colour},
        "bordercolor": "#fafafa",
        "steps": [
            {"range": [range["min"], indicator_value], "color": bar_colour},
            {"range": [indicator_value, range["max"]], "color": "#D4D4D4"},
        ],

    }
    #Make the meter plot
    fig = go.Figure(
        data=[
            go.Indicator(
                value=indicator_value,
                mode="gauge+number",
                gauge= gauge,
                domain={"row": 0, "column": 100},
                #Add percentage value bellow the meter
                number={"suffix": "%", "font": {"size": 30}},
            )
        ]
    )

    #Add value annotation
    fig.add_annotation(
        x=0.49,
        y=0.45,
        text="{:,}".format(absolute_value),
        font=dict(size=15),
        showarrow=False,
    )
    #Some styling
    fig.update_layout(
        margin=dict(l=0, r=0, t=1, b=0),
        height=120,
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

#Bar plot of summary of orgs contribution to deployment for each country
def country_orgs_bar_plot(df, country_order=None, condensed=False):
    # To supress Settings with copy warning
    pd.options.mode.chained_assignment = None
    df.rename(columns={"Organisation": "Command"}, inplace=True)

    #If one country make bars horizontal
    if len(df["Country"].unique()) == 1:
        #Select which data to plot on which axis, graph orientation and axes styling
        x = "Deployed"
        y ="Command"
        orientation = "h"
        xaxis_title = "Deployed"
        yaxis_title = None
        xaxis_tickformat = ","
        yaxis_tickformat = None
        xaxis = None
        # Hover template
        hover_template = "<b>Command: %{customdata[0]}</b><br>"\
                         + "Deployed: %{x:,} <br>"\
                         + "Share: %{customdata[1]:.3}% <br>"\
                         + "<extra></extra>"

    #If more than one country, make bard vertical
    else:
        # Select which data to plot on which axis, graph orientation and axes styling
        x = "Country"
        y = "Deployed"
        orientation = None
        xaxis_title = None
        yaxis_title = "Deployed"
        xaxis_tickformat = None
        yaxis_tickformat = ","
        #Order bars from highest deployment to lowest
        xaxis = {"categoryorder": "array", "categoryarray": country_order}
        #Hover template
        hover_template = "<b>Country: %{x}</b><br>"\
                         + "<b>Command: %{customdata[0]}</b><br>"\
                         + "Deployed: %{y:,} <br>"\
                         + "Share: %{customdata[1]:.3}% <br>"\
                         + "<extra></extra>"

    #Create figure with all styling defined above
    fig = px.bar(
        df,
        x=x,
        y=y,
        color="Command",
        orientation=orientation,
        color_discrete_map={
            **constants.organisation_colors,
            **constants.country_colors,
        },
        custom_data=["Command", "Percentage of Total Deployment"],
    )
    fig.update_layout(
        margin=dict(l=100, r=0, t=0, b=0),
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        xaxis_tickformat=xaxis_tickformat,
        yaxis_tickformat=yaxis_tickformat,
        xaxis=xaxis,
    )
    fig.update_traces(hovertemplate=hover_template)

    if len(df["Country"].unique()) == 2:
        fig.update_layout(
            xaxis_tickangle=0,
        )
    #If graoh should be condensed change styling
    if condensed:
        fig.update_layout(
            font=dict(
                size=12,
            ),
            xaxis_tickangle=0,
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
        height=650,
    )

    return fig


#Cards with summary plots
def summary_graph_card(
    title,
    text,
    card_info,
    graph,
    modal_id=None,
    full_graph=None,
    title_colour=constants.colors["cardName"],
    title_colour_highlighted=False
):

    #Title styling for the card
    title_text = html.H5(str(title),
                         style={
                             "color": title_colour,
                             "display": "inline-block",
                             "margin-right": "1px"
                         }
                         )

    #If want to highlight the title (i.e lrger font size and red colour)
    if title_colour_highlighted:
        title_colour = constants.colors["title"]
        title_text = html.H4(str(title),
                             style={
                                 "color": title_colour,
                                 "display": "inline-block",
                                 "margin-right": "1px"
                             }
                             )

    #Define expand_button&modal_overlay as empty
    expand_button = ""
    modal_overlay = ""
    #If want to include the full graph in modal (i.e if more than 5 countries selected)
    if full_graph is not None:
        modal_overlay = modal_overlay_template(modal_id, full_graph)
        expand_button = html.I(
            className="fas fa-plus-square",
            id=f"expand_{modal_id}",
            style={"text-align": "right", "margin-right": "10px"},
        )

    #Define info cricle
    info_circle = ""
    #If want to include info about the card
    if card_info is not None:
        info_circle = dbc.Col(
            [
                expand_button,
                html.I(
                    className="fas fa-regular fa-circle-info",
                    id=f"target_{title}",
                    style={"text-align": "right"},
                ),
                dbc.Tooltip(card_info, target=f"target_{title}"),
                modal_overlay,
            ],
            style={"text-align": "right"},
        )

    #Make the card
    card = dbc.CardBody(
        [
            #Row with title, info circle and expand button
            dbc.Row(
                [
                    dbc.Col(
                        [
                            title_text
                        ],
                        className="col-9",
                    ),
                    info_circle,
                ]
            ),
            #Subtitle
            html.H6(
                text,
                className="card-text",
            ),
            #Graph
            dcc.Graph(figure=graph, config=graph_config) if graph else "",
        ]
    )

    return card

#Card for two graphs (i.e two meter plots when 2 countries selected)
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

#Template for modal (full graph pop-up)
def modal_overlay_template(id, graph):
    modal = dbc.Modal(
        [
            dbc.ModalBody(
                dcc.Graph(figure=graph, config=graph_config), id=f"expand-{id}-md"
            ),
            dbc.ModalFooter(dbc.Button("Close", id=f"expand-{id}-close")),
        ],
        id=f"full-{id}-graph",
        size="xl",
    )

    return modal
