import pandas as pd
import numpy as np
from collections import Counter

from dash import Input, Output, State, exceptions
import plotly.express as px
import plotly.graph_objects as go

from .server import app
from . import constants, card_texts
from .plotting_functions import (
    horizontal_bar_plot,
    percentage_calculate,
    summary_graph_card,
    plot_graph_card,
    meter_plot,
    country_orgs_bar_plot,
    comparison_summary_graph_card,
    summary_graph_card_small,
    modal_overlay_template,
)

from . import index

# data
from .app import df_deployments, df_presence, mapbox_access_token, ROOT

# index.calculate_mdi(df_deployments)

# default store
selected_countries_default = pd.Series(
    data=dict.fromkeys(
        list(df_deployments.sort_values(by="Country").Country.unique()), True
    )
)
selected_year_default = pd.DataFrame(data={"year": [2021]})


def update_map(selected_year, selected_countries, military_presence):
    def get_data(dfn, name):
        data = go.Scattermapbox(
            name=name,
            lat=dfn.Lat,
            lon=dfn.Lon,
            mode="markers",
            marker=go.scattermapbox.Marker(
                allowoverlap=True,
                color=dfn.Color,
                opacity=0.5,
                # size=np.log2(dfp.Deployed, out=np.zeros_like(
                #     dfp.Deployed), where=(dfp.Deployed != 0)).values,
                size=dfn.Deployed,
                sizeref=20,
                sizemin=2,
            ),
            customdata=dfn,
            hovertemplate="<b>Country: %{customdata[5]}</b><br>"
            + "Theatre: %{customdata[2]} <br>"
            + "Deployed: %{customdata[9]:,} <br>"
            + "Command: %{customdata[6]} <br>"
            + "Operation: %{customdata[7]} <br>"
            + "<extra></extra>",
            showlegend=False,
        )
        return data

    def get_presence_data(dfn, name):
        data = go.Scattermapbox(
            name=name,
            lat=dfn.Lat,
            lon=dfn.Lon,
            mode="markers",
            marker=go.scattermapbox.Marker(
                allowoverlap=True,
                symbol="triangle",
                color=dfn.Color,
            ),
            customdata=dfn,
            hovertemplate="<b>Country: %{customdata[5]}</b><br>"
            + "Theatre: %{customdata[2]} <br>"
            + "Deployed: %{customdata[9]} <br>"
            + "Command: %{customdata[6]} <br>"
            + "<extra></extra>",
            showlegend=False,
        )
        return data

    hoverlabel = dict(font_size=16)

    mapbox = dict(
        accesstoken=mapbox_access_token,
        center=dict(lat=24, lon=0),
        zoom=1.5,
        style="light",
    )

    layout = dict(
        title="",
        hovermode="closest",
        height=600,
        margin=go.layout.Margin(l=0, r=0, t=0, b=0),
        mapbox=mapbox,
        hoverlabel=hoverlabel,
        uirevision="perservere",
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # filter and sort
    dfp = df_deployments.query("Country in @selected_countries")
    dfp = dfp[dfp["Year"] == selected_year].sort_values(by="Country")

    dfp_presence = df_presence.query("Country in @selected_countries")
    dfp_presence = dfp_presence[dfp_presence["Year"] == selected_year].sort_values(
        by="Country"
    )

    # generate
    data = [
        get_data(
            dfp.loc[(dfp["Country"] == country)],
            country,
        )
        for country in dfp["Country"].unique()
    ]

    if military_presence:
        data = data + [
            get_presence_data(
                dfp_presence.loc[(dfp_presence["Country"] == country)],
                country,
            )
            for country in dfp_presence["Country"].unique()
        ]

    figure = go.Figure(
        data=data,
        layout=layout,
    )

    return figure


def update_line_plot(dfp):
    def get_data(dfn, name):
        dfg = dfn.groupby(["Year"])["Deployed"].sum()
        data = go.Scatter(
            x=dfg.index,
            y=dfg.values,
            name=name,
            showlegend=False,
            line=dict(color=dfn.Color.iloc[0]),
            hovertemplate=f"<b>Country: {name}</b><br>"
            + "Deployed: %{y:,}"
            + "<extra></extra>",
        )
        return data

    data = [
        get_data(dfp[dfp["Country"] == country], country)
        for country in dfp["Country"].unique()
    ]

    figure = go.Figure(data=data)
    figure.update_layout(
        margin=dict(l=90, r=0, t=0, b=0),
        height=340,
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Deployed",
        yaxis_title_standoff=90,
        yaxis_tickformat=",",
    )
    figure.update_yaxes(
        title_standoff=constants.theme["title_standoff"],
        tickfont_size=constants.theme["tickfont_size"],
        titlefont_size=constants.theme["titlefont_size"],
    )
    figure.update_xaxes(
        title_standoff=constants.theme["title_standoff"],
        tickfont_size=constants.theme["tickfont_size"],
        dtick=1,
    )

    # TODO: figure out a way to prevent overlappping labels BUT MAYBE NOT A GOOD IDEA
    # if len(dfp["Country"].unique()) > 100:
    #    country_sum = (
    #        dfp.groupby(["Country"])["Deployed"]
    #        .sum()
    #        .sort_values(ascending=False)
    #    )
    #    country_list = list(country_sum.head(10).index)
    # else:
    #    country_list = dfp["Country"].unique()

    country_list = dfp["Country"].unique()

    figure.for_each_trace(
        lambda f: figure.add_annotation(
            x=f.x[-1] + 0.1,
            y=f.y[-1],
            text=f.name,
            font_color=f.line.color,
            xanchor="left",
            showarrow=False,
            font_size=constants.theme["titlefont_size"],
        )
        if f.name in country_list
        else None
    )

    card = plot_graph_card(
        card_texts.dot_title,
        card_texts.dot_under_title,
        card_texts.dot_info_circle,
        figure,
    )

    return card


def update_sunburst_plot(dfp):
    dfm = dfp.groupby(["Organisation", "MissionName"])["Deployed"].sum()
    dfm = dfm.to_frame().reset_index()

    dfo = dfp.groupby(["Organisation"])["Deployed"].sum()

    orgs = list(dfm.Organisation.unique())

    data = go.Sunburst(
        ids=orgs
        + [x + y for x, y in zip(list(dfm.Organisation), list(dfm.MissionName))],
        labels=orgs + list(dfm.MissionName),
        parents=[""] * len(orgs) + list(dfm.Organisation),
        values=list(dfo) + list(dfm.Deployed),
        branchvalues="total",
        marker=go.sunburst.Marker(
            colors=[
                constants.organisation_colors.get(
                    org,
                    constants.country_colors.get(
                        org, constants.organisation_colors.get("default")
                    ),
                )
                for org in orgs
            ]
        ),
        insidetextorientation="radial",
        hovertemplate="<b> %{label} </b><br>"
        + "Deployed: %{value:,}<br>"
        + "Share: %{percentParent:.3p}<br>"
        + "<extra></extra>",
    )
    figure = go.Figure(data=data)
    figure.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=500,
    )

    if len(dfp["Country"].unique()) == 1:
        card_under_title = f"FOR {dfp['Country'].unique()[0]}"
    else:
        card_under_title = card_texts.sbp_under_title

    card = plot_graph_card(
        card_texts.sbp_title,
        card_under_title,
        card_texts.sbp_info_circle,
        figure,
    )

    return card


def update_population_plot(df_deploy, df_population, year):
    df = pd.DataFrame(columns=["Country Name", "Deployment Per Capita"])

    # Calculate deployment per 100,000 capita for each country
    for country in df_population["Country"].unique():
        total_deployed = df_deploy[df_deploy["Country"] == country]["Deployed"].sum()
        population = int(df_population[df_population["Country"] == country][year])
        country_name = constants.country_codes[country]

        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    [
                        [
                            country_name,
                            percentage_calculate(total_deployed, population, 100000),
                        ]
                    ],
                    columns=["Country Name", "Deployment Per Capita"],
                ),
            ]
        )

    df = df.sort_values(by=["Deployment Per Capita"], ascending=False)
    deployment_mean = round(df["Deployment Per Capita"].mean(), 1)

    # If more than 5 countries, select top 5
    if df.shape[0] > 5:
        df_top_5 = df.head(5)
        condensed = True

        # Create figures also in modal
        fig = horizontal_bar_plot(
            df_top_5["Deployment Per Capita"].iloc[::-1].values,
            df_top_5["Country Name"].iloc[::-1].values,
            df_top_5["Deployment Per Capita"].iloc[::-1].values,
            20,
            condensed=condensed,
        )

        full_graph = horizontal_bar_plot(
            df["Deployment Per Capita"].iloc[::-1].values,
            df["Country Name"].iloc[::-1].values,
            df["Deployment Per Capita"].iloc[::-1].values,
            20,
        )

        modal_id = "population"

    else:

        # Create only page figure, ignore modal
        fig = horizontal_bar_plot(
            df["Deployment Per Capita"].iloc[::-1].values,
            df["Country Name"].iloc[::-1].values,
            df["Deployment Per Capita"].iloc[::-1].values,
            20,
        )

        full_graph = None

        modal_id = None

    # Create a card
    # If only 1 country, smaller height
    if df.shape[0] == 1:
        fig.update_layout(height=144)
    elif df.shape[0] == 2:
        fig.update_layout(height=164)
    else:
        fig.update_layout(height=144)

    card = plot_graph_card(
        card_texts.dpc_under_title,
        "",
        card_texts.dpc_info_circle,
        fig,
        modal_id=modal_id,
        full_graph=full_graph,
    )
    return card


def update_active_plot(df_deploy, df_active):
    df = pd.DataFrame(columns=["Country Name", "Active Personnel"])

    for country in df_active["Country"].unique():
        total_deployed = df_deploy[df_deploy["Country"] == country]["Deployed"].sum()
        active_personnel = int(
            df_active[df_active["Country"] == country]["Personnel_Count"]
        )
        country_name = constants.country_codes[country]

        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    [
                        [
                            country_name,
                            percentage_calculate(total_deployed, active_personnel, 100),
                            total_deployed,
                        ]
                    ],
                    columns=[
                        "Country Name",
                        "Percent of Active Personnel",
                        "Total Deployed",
                    ],
                ),
            ]
        )

    df = df.sort_values(by=["Percent of Active Personnel"], ascending=False)
    active_mean = round((df["Percent of Active Personnel"].mean()), 1)

    # If more than 5 countries, select top 5
    if df.shape[0] > 5:
        df_top_5 = df.head(5)
        condensed = True

        # Create figures also in modal
        fig = horizontal_bar_plot(
            df_top_5["Percent of Active Personnel"].iloc[::-1].values,
            df_top_5["Country Name"].iloc[::-1].values,
            df_top_5["Percent of Active Personnel"].iloc[::-1].values,
            100,
            percentage=True,
            condensed=condensed,
        )

        full_graph = horizontal_bar_plot(
            df["Percent of Active Personnel"].iloc[::-1].values,
            df["Country Name"].iloc[::-1].values,
            df["Percent of Active Personnel"].iloc[::-1].values,
            100,
            percentage=True,
        )

        modal_id = "active"

    else:

        # Create only page figure, ignore modal
        fig = horizontal_bar_plot(
            df["Percent of Active Personnel"].iloc[::-1].values,
            df["Country Name"].iloc[::-1].values,
            df["Percent of Active Personnel"].iloc[::-1].values,
            100,
            percentage=True,
        )

        full_graph = None

        modal_id = None

    # Create a card
    # If only 1 country, smaller height
    if df.shape[0] == 1:
        fig.update_layout(height=144)
    elif df.shape[0] == 2:
        fig.update_layout(height=164)
    else:
        fig.update_layout(height=144)

    card = plot_graph_card(
        card_texts.dap_under_title,
        "",
        card_texts.dap_info_circle,
        fig,
        modal_id=modal_id,
        full_graph=full_graph,
    )
    return card


def update_deployed_meter_plot(df_deploy):
    df = df_deploy.groupby(["Theatre"])["Deployed"].sum()
    total_deployed = df_deploy["Deployed"].sum()

    # Theatre with the highest percentage deployment
    highest_percentage = percentage_calculate(df.max(), total_deployed, scaling=100)

    # Create a figure and a card
    fig = meter_plot(highest_percentage, df.max(), {"min": 0, "max": 100})
    card = summary_graph_card_small(
        df.idxmax(),
        card_texts.tdm_under_title,
        card_texts.tdm_info_circle,
        fig,
    )

    return card


def update_two_deployment_meter_plots(df_deploy):
    top_theatres = []

    for country in df_deploy["Country"].unique():
        total_deployed = df_deploy[df_deploy["Country"] == country]["Deployed"].sum()
        country_theatres = (
            df_deploy[df_deploy["Country"] == country]
            .groupby(["Theatre"])["Deployed"]
            .sum()
        )
        top_theatre = country_theatres[country_theatres == country_theatres.max()]
        top_theatre_percentage = percentage_calculate(
            country_theatres.max(), total_deployed, scaling=100
        )
        fig = meter_plot(
            top_theatre_percentage,
            country_theatres.max(),
            {"min": 0, "max": 100},
            bar_colour=constants.country_colors[country],
        )
        top_theatres.append(
            {
                "Country": country,
                "Title": top_theatre.index,
                "Title colour": constants.country_colors[country],
                "Text": card_texts.tdm_under_title + f" of {country}",
                "Graph": fig,
            }
        )
    card = comparison_summary_graph_card(
        top_theatres[0], top_theatres[1], card_info=card_texts.tdm_info_circle
    )
    return card


def update_total_deployment_plot(df_deploy):
    df = df_deploy.copy()
    condensed = False

    country_sum = (
        df_deploy.groupby(["Country"])["Deployed"].sum().sort_values(ascending=False)
    )

    # query top 5 organisations to include in the graph
    top_orgs = list(
        df.groupby(["Organisation"])
        .sum()
        .sort_values(by="Deployed", ascending=False)
        .head(5)
        .index
    )

    # Rename all other orgs to "Other" and sum
    if len(df_deploy["Organisation"].unique()) > 5:
        df.loc[~df["Organisation"].isin(top_orgs), "Organisation"] = "Other"
    df = df.groupby(["Country", "Organisation"])["Deployed"].sum().reset_index()

    def _calc_total_deploy_precentage(row):
        percentage = percentage_calculate(
            row["Deployed"],
            country_sum[country_sum.index == row["Country"]].values[0],
            scaling=100,
        )
        return percentage

    df["Percentage of Total Deployment"] = df.apply(
        _calc_total_deploy_precentage, axis=1
    )

    df = df.sort_values(by="Deployed", ascending=False)

    # Select top 5 deployment countries
    if len(df_deploy["Country"].unique()) > 5:
        country_list = list(country_sum.head(5).index)
        df_top_5 = df.query("Country in @country_list")
        condensed = True

        # Create figures also in modal
        fig = country_orgs_bar_plot(
            df_top_5, country_order=country_list, condensed=condensed
        )

        full_graph = country_orgs_bar_plot(df, country_order=country_sum.index)

        modal_id = "total-deployment"

    else:
        # Create only page figure, ignore modal
        fig = country_orgs_bar_plot(df, country_order=country_sum.index)
        modal_id = (None,)
        full_graph = None

    # Update figure height and create a card
    fig.update_layout(height=250)

    if len(df["Country"].unique()) == 1:
        card_under_title = f"FOR {df['Country'].unique()[0]}"

    else:
        card_under_title = card_texts.tdop_under_title

    card = plot_graph_card(
        card_texts.tdop_title,
        card_under_title,
        card_texts.tdop_info_circle,
        fig,
        modal_id=modal_id,
        full_graph=full_graph,
    )
    return card


def update_orgs_bar_plot(df_deploy):
    df = df_deploy.copy()
    total_deployed = df_deploy["Deployed"].sum()

    # Query top 5 organisations, rest goes under other
    top_orgs = (
        df.groupby(["Organisation"])
        .sum()
        .sort_values(by="Deployed", ascending=False)
        .head(5)
    )

    # Orgs names, deployments and colours
    deployed_numbers = list(top_orgs["Deployed"])
    deployed_names_orgs = list(top_orgs.index)

    if len(df_deploy["Organisation"].unique()) > 5:
        deployed_names_orgs.append("Other")
        other_orgs = total_deployed - top_orgs["Deployed"].sum()
        deployed_numbers.append(other_orgs)

    deployment_percentage = []
    # Percentage of organisation deployment to total deployment
    for number in deployed_numbers:
        percentage = percentage_calculate(number, total_deployed, 100)
        if percentage < 1:
            deployment_percentage.append(percentage)
        else:
            deployment_percentage.append(int(percentage))

    colours = [
        constants.organisation_colors.get(
            org,
            constants.country_colors.get(
                org, constants.organisation_colors.get("default")
            ),
        )
        for org in deployed_names_orgs
    ]

    # Create a figure and a card
    fig = horizontal_bar_plot(
        deployment_percentage[::-1],
        deployed_names_orgs[::-1],
        deployment_percentage[::-1],
        max_value=100,
        percentage=True,
        colour=colours[::-1],
    )
    fig.update_layout(height=137)
    card = summary_graph_card(
        "{:,}".format(total_deployed),
        card_texts.tdp_under_title,
        card_texts.tdp_info_circle,
        fig,
    )
    return card


def update_mdi_plot(dfp):
    def get_data(dfn, name):
        data = go.Scatter(
            x=dfn["Year"],
            y=dfn["MDI"],
            name=name,
            showlegend=False,
            line=dict(color=constants.country_colors[name]),
            hovertemplate=f"<b>Country: {name}</b><br>"
            + "MDI: %{y}"
            + "<extra></extra>",
        )
        return data

    mdi = None
    for year in dfp["Year"].unique():
        dfs = index.calculate_mdi(df_deployments, year)
        dfs["Year"] = year
        if mdi is None:
            mdi = dfs
        else:
            mdi = pd.concat([mdi, dfs])

    data = [
        get_data(mdi[mdi["Country"] == country], country)
        for country in dfp["Country"].unique()
    ]

    figure = go.Figure(data=data)
    figure.update_layout(
        margin=dict(l=50, r=0, t=0, b=0),
        height=340,
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="MDI",
        yaxis_title_standoff=30,
        yaxis_tickformat=",",
    )
    figure.update_yaxes(
        title_standoff=constants.theme["title_standoff"],
        tickfont_size=constants.theme["tickfont_size"],
        titlefont_size=constants.theme["titlefont_size"],
    )
    figure.update_xaxes(
        title_standoff=constants.theme["title_standoff"],
        tickfont_size=constants.theme["tickfont_size"],
        dtick=1,
    )

    country_list = dfp["Country"].unique()

    figure.for_each_trace(
        lambda f: figure.add_annotation(
            x=f.x[-1] + 0.1,
            y=f.y[-1],
            text=f.name,
            font_color=f.line.color,
            xanchor="left",
            showarrow=False,
            font_size=constants.theme["titlefont_size"],
        )
        if f.name in country_list
        else None
    )

    card = plot_graph_card(
        card_texts.mdip_title,
        card_texts.mdip_under_title,
        card_texts.mdip_info_circle,
        figure,
    )

    return card


def update_dashboard(selected_countries, year):
    dfp = df_deployments
    df_active = pd.read_excel(ROOT + "data/MDVA_ActiveDuty.xlsx")
    df_population = pd.read_csv(ROOT + "data/MDVA_Population.csv", delimiter=",")

    if not selected_countries:
        raise exceptions.PreventUpdate

    dfp = dfp.query("Country in @selected_countries")
    df_active = df_active.query("Country in @selected_countries")
    df_population = df_population.query("Country in @selected_countries")
    # TODO: maybe unnecessary to choose which one

    dfp_year = dfp[dfp["Year"] == int(year)]

    deployments_over_time_card = update_line_plot(dfp)
    sunburst_card = update_sunburst_plot(dfp_year)
    population_card = update_population_plot(dfp_year, df_population, str(year))
    active_card = update_active_plot(
        dfp_year, df_active[df_active["Year"] == int(year)]
    )
    deploy_meter_card = update_deployed_meter_plot(dfp_year)
    orgs_countries_card = update_total_deployment_plot(dfp_year)
    orgs_bar_card = update_orgs_bar_plot(dfp_year)
    mdi_card = update_mdi_plot(dfp)

    if len(selected_countries) == 1:
        return (
            deployments_over_time_card,
            sunburst_card,
            population_card,
            active_card,
            deploy_meter_card,
            orgs_countries_card,
            orgs_bar_card,
            mdi_card,
        )

    elif len(selected_countries) == 2:
        return (
            deployments_over_time_card,
            sunburst_card,
            population_card,
            active_card,
            update_two_deployment_meter_plots(dfp_year),
            orgs_countries_card,
            orgs_bar_card,
            mdi_card,
        )

    else:
        return (
            deployments_over_time_card,
            sunburst_card,
            population_card,
            active_card,
            deploy_meter_card,
            orgs_countries_card,
            orgs_bar_card,
            mdi_card,
        )


@app.callback(
    Output(component_id="card-line", component_property="children"),
    Output(component_id="card-sunburst", component_property="children"),
    Output(component_id="card-population", component_property="children"),
    Output(component_id="card-active", component_property="children"),
    Output(component_id="card-theatre", component_property="children"),
    Output(component_id="card-countries-orgs", component_property="children"),
    Output(component_id="card-bar-orgs", component_property="children"),
    Output(component_id="card-mdi", component_property="children"),
    Input(component_id="selected-countries", component_property="data"),
    Input(component_id="selected-year", component_property="data"),
)
def reload_dashboard(selected_countries, selected_year):
    selected_year = pd.read_json(selected_year)["year"].iloc[0]

    return update_dashboard(selected_countries, selected_year)


@app.callback(
    Output(component_id="selected-year", component_property="data"),
    Output(component_id="graph-map", component_property="figure"),
    Output(component_id="selected-countries", component_property="data"),
    Input(component_id="year-slider", component_property="value"),
    Input(component_id="country-filter", component_property="value"),
    Input(component_id="military-presence-switch", component_property="value"),
    State(component_id="graph-map", component_property="relayoutData"),
)
def update_filters(actual_year, country_selection, military_presence, data):
    zoom = 1.5
    center = dict(lat=24, lon=0)
    if data:
        zoom = data.get("mapbox.zoom", 1.5)
        center = data.get("mapbox.center", dict(lat=24, lon=0))

    figure = update_map(actual_year, country_selection, military_presence)
    figure.update_layout(mapbox_zoom=zoom, mapbox_center=center)

    selected_year = selected_year_default
    selected_year["year"].iloc[0] = actual_year

    return (
        selected_year.to_json(),
        figure,
        country_selection,
    )


# Population expand graph
@app.callback(
    Output("full-population-graph", "is_open"),
    [
        Input("expand_population", "n_clicks"),
        Input("expand-population-close", "n_clicks"),
    ],
    [State("full-population-graph", "is_open")],
)
def population_toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Active expand graph
@app.callback(
    Output("full-active-graph", "is_open"),
    [Input("expand_active", "n_clicks"), Input("expand-active-close", "n_clicks")],
    [State("full-active-graph", "is_open")],
)
def active_toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# Total deployment expand graph
@app.callback(
    Output("full-total-deployment-graph", "is_open"),
    [
        Input("expand_total-deployment", "n_clicks"),
        Input("expand-total-deployment-close", "n_clicks"),
    ],
    [State("full-total-deployment-graph", "is_open")],
)
def total_deployment_toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
