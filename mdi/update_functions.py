import pandas as pd

from dash import Input, Output, State, exceptions
import plotly.graph_objects as go

#Graph functions and styling
from .server import app
from . import constants, card_texts
from .plotting_functions import (
    horizontal_bar_plot,
    percentage_calculate,
    summary_graph_card,
    meter_plot,
    country_orgs_bar_plot,
    comparison_summary_graph_card,
    line_chart
)

# data
from .app import df_deployments, df_presence, mapbox_access_token, ROOT

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

    query = "Country in @selected_countries & Year == @selected_year"

    # filter and sort
    dfp = df_deployments.query(query).sort_values(by="Country")

    dfp_presence = df_presence.query(query).sort_values(by="Country")

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
    #List of countries
    country_list = dfp["Country"].unique()

    data = [
        get_data(dfp[dfp["Country"] == country], country)
        for country in country_list
    ]

    #Make figure
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

    #Add annotation for each line
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

    #Make a card
    card = summary_graph_card(
        card_texts.dot_title,
        card_texts.dot_under_title,
        card_texts.dot_info_circle,
        figure,
    )

    return card


def update_sunburst_plot(dfp):
    #Filter numbers by organisations and mission
    dfm = dfp.groupby(["Organisation", "MissionName"])["Deployed"].sum()
    dfm = dfm.to_frame().reset_index()

    dfo = dfp.groupby(["Organisation"])["Deployed"].sum()

    #List of orgs
    orgs = list(dfm.Organisation.unique())

    #Make a plot
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
    )

    #Change subtitle if only one country selected
    if len(dfp["Country"].unique()) == 1:
        card_under_title = f"FOR {dfp['Country'].unique()[0]}"
    else:
        card_under_title = card_texts.sbp_under_title

    #Make card
    card = summary_graph_card(
        card_texts.sbp_title,
        card_under_title,
        card_texts.sbp_info_circle,
        figure,
    )

    return card


def update_population_plot(df_deployment_capita):
    #Sort data
    df = df_deployment_capita.sort_values(by=["Deployment Per Capita"], ascending=False)

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
    #Graph height to level out cards in one row
    if df.shape[0] == 1:
        fig.update_layout(height=134)
    else:
        fig.update_layout(height=164)

    card = summary_graph_card(
        card_texts.dpc_under_title,
        "",
        card_texts.dpc_info_circle,
        fig,
        modal_id=modal_id,
        full_graph=full_graph,
    )
    return card


def update_active_plot(df_active_personnel):
    #Sort data
    df = df_active_personnel.sort_values(by=["Percent of Active Personnel"], ascending=False)

    #Graph in modal (only if more than 5 countries selected)
    full_graph = None
    modal_id = None

    # If more than 5 countries, select top 5
    if df.shape[0] > 5:

        full_graph = horizontal_bar_plot(
            df["Percent of Active Personnel"].iloc[::-1].values,
            df["Country Name"].iloc[::-1].values,
            df["Percent of Active Personnel"].iloc[::-1].values,
            100,
            percentage=True,
        )

        modal_id = "active"

    df = df.head(5)
    # Figure in the card
    fig = horizontal_bar_plot(
        df["Percent of Active Personnel"].iloc[::-1].values,
        df["Country Name"].iloc[::-1].values,
        df["Percent of Active Personnel"].iloc[::-1].values,
        100,
        percentage=True
    )

    # Create a card
    #Graph height to level out cards in one row
    if df.shape[0] == 1:
        fig.update_layout(height=134)
    else:
        fig.update_layout(height=164)

    card = summary_graph_card(
        card_texts.dap_under_title,
        "",
        card_texts.dap_info_circle,
        fig,
        modal_id=modal_id,
        full_graph=full_graph,
    )
    return card


def update_deployed_meter_plot(df_deploy, df_deploy_all_years):
    df = df_deploy.groupby(["Theatre"])["Deployed"].sum()
    total_deployed = df_deploy["Deployed"].sum()

    # Theatre with the highest percentage deployment
    highest_percentage = percentage_calculate(df.max(), total_deployed, scaling=100)

    # Create a figure and a card
    fig = meter_plot(highest_percentage, df.max(), {"min": 0, "max": 100})

    #Graph height to level out cards in one row
    if df_deploy["Country"].unique().shape[0] == 1:
        fig.update_layout(height=134)
    else:
        fig.update_layout(height=164)

    #Create a figure to put inside the modal
    #Query deployment to the top theatre, groups deployment by years and sum total deployment for each year
    top_theatre_timeseries = df_deploy_all_years.query(f'Theatre == @df.idxmax()').groupby(["Year"])["Deployed"].sum()
    figure_dict = {"x":top_theatre_timeseries.index.values,
                   "y":top_theatre_timeseries.values,
                   "title": f"Total deployment to {df.idxmax()} for all selected countries over time",
                   "x_label": "Year",
                   "y_label": "Total deployment",
                   "colour":constants.red}
    fig_modal = line_chart([figure_dict])


    card = summary_graph_card(
        df.idxmax(),
        card_texts.tdm_under_title,
        card_texts.tdm_info_circle,
        fig,
        modal_id="top-theatre",
        full_graph=fig_modal,
        title_colour_highlighted=True
    )

    return card


def update_two_deployment_meter_plots(df_deploy):
    top_theatres = []

    for country in df_deploy["Country"].unique():
        #Calculate total deployment
        total_deployed = df_deploy.query("Country == @country")["Deployed"].sum()
        #Calculate deployments for each theatre
        country_theatres = (
            df_deploy.query("Country == @country")
            .groupby(["Theatre"])["Deployed"]
            .sum()
        )
        #Find top theatre and its percentual contribution
        top_theatre = country_theatres[country_theatres == country_theatres.max()]
        top_theatre_percentage = percentage_calculate(
            country_theatres.max(), total_deployed, scaling=100
        )
        #Make meter plot
        fig = meter_plot(
            top_theatre_percentage,
            country_theatres.max(),
            {"min": 0, "max": 100},
            bar_colour=constants.country_colors[country],
        )

        # Graph height to level out cards in one row
        fig.update_layout(height=164)

        top_theatres.append(
            {
                "Country": country,
                "Title": top_theatre.index,
                "Title colour": constants.country_colors[country],
                "Text": card_texts.tdm_under_title + f" of {country}",
                "Graph": fig,
            }
        )
    #Make card
    card = comparison_summary_graph_card(top_theatres[0], top_theatres[1], card_info=card_texts.tdm_info_circle )
    return card


def update_total_deployment_plot(df_deployment_top_org):

    country_deployment_sum = (df_deployment_top_org.groupby(["Country"])["Deployed"].sum().sort_values(ascending=False))
    df_deployment_top_org = df_deployment_top_org.sort_values(by="Deployed", ascending=False)

    #Select top 5 orgs
    top5_orgs = list(
        df_deployment_top_org.groupby(["Organisation"])
        .sum()
        .sort_values(by="Deployed", ascending=False)
        .head(5)
        .index
    )

    # If more than 5 orgs, rename all other orgs not in top 5 to "Other"
    if len(df_deployment_top_org["Organisation"].unique()) > 5:
        df_deployment_top_org.loc[~df_deployment_top_org["Organisation"].isin(top5_orgs[:5]),
                                  "Organisation"] = "Other"

    df_deployment_top_org = df_deployment_top_org.sort_values(by="Deployed", ascending=False)
    # If more than 5 countries create a card with modal where you can see all countries
    if len(df_deployment_top_org["Country"].unique()) > 5:
        country_list = list(country_deployment_sum.head(5).index)
        df_top_5 = df_deployment_top_org.query("Country in @country_list")
        condensed = True

        # Create figures also in modal
        fig = country_orgs_bar_plot(
            df_top_5, country_order=country_list, condensed=condensed
        )
        #Graph containing all coutnries
        full_graph = country_orgs_bar_plot(df_deployment_top_org, country_order=country_deployment_sum.index)

        modal_id = "total-deployment"

    else:
        # Create only page figure, ignore modal
        fig = country_orgs_bar_plot(df_deployment_top_org, country_order=country_deployment_sum.index)
        modal_id = (None,)
        full_graph = None

    # Update figure height and create a card
    fig.update_layout(height=250)

    #Change card subtitle if only one country selected
    if len(df_deployment_top_org["Country"].unique()) == 1:
        card_under_title = f"FOR {df_deployment_top_org['Country'].unique()[0]}"

    else:
        card_under_title = card_texts.tdop_under_title

    #Make card
    card = summary_graph_card(
        card_texts.tdop_title,
        card_under_title,
        card_texts.tdop_info_circle,
        fig,
        modal_id=modal_id,
        full_graph=full_graph,
    )
    return card


def update_orgs_bar_plot(df_deploy):
    #Calculate total deployment
    total_deployed = df_deploy["Deployed"].sum()

    # Query top 5 organisations, rest goes under other
    top_orgs = (
        df_deploy.groupby(["Organisation"])
        .sum()
        .sort_values(by="Deployed", ascending=False)
        .head(5)
    )

    # List of orgs names, deployments and colours
    deployed_numbers = list(top_orgs["Deployed"])
    deployed_names_orgs = list(top_orgs.index)

    #If more than 5 orgs, rest goes under other
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
    #Orgs colours to use for bar graph
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
    #summary_graph_card
    card = summary_graph_card(
        "{:,}".format(total_deployed),
        card_texts.tdp_under_title,
        card_texts.tdp_info_circle,
        fig,
        title_colour_highlighted=True
    )
    return card


def update_mdi_plot(mdi):
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
    #Get all countries
    country_list = mdi["Country"].unique()

    #Make the mdi summary figure
    data = [
        get_data(mdi.query("Country== @country"), country)
        for country in country_list
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

    #Add annotation to each line
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

    card = summary_graph_card(
        card_texts.mdip_title,
        card_texts.mdip_under_title,
        card_texts.mdip_info_circle,
        figure,
    )

    return card


def update_dashboard(selected_countries, year):
    #Load data
    #Deployments data
    dfp = df_deployments
    #MDI values for all countries and years
    df_mdi = pd.read_csv(ROOT + "data/mdi.csv", delimiter=",")
    #Active personnel data for all countries and years
    df_active_personnel = pd.read_csv(ROOT + "data/active_personnel.csv", delimiter=",")
    #Deployments per capita for all countries and years
    df_deployment_capita = pd.read_csv(ROOT + "data/deployment_per_capita.csv", delimiter=",")
    #Top oragnisations for each country per year
    df_deployment_top_org = pd.read_csv(ROOT + "data/top_organisations.csv", delimiter=",")

    if not selected_countries:
        raise exceptions.PreventUpdate

    #Query data based on chosen countries and year
    dfp = dfp.query("Country in @selected_countries")
    df_active_personnel = df_active_personnel.query("Country in @selected_countries & Year == @year")
    df_deployment_capita = df_deployment_capita.query("Country in @selected_countries & Year == @year")
    df_deployment_top_org = df_deployment_top_org.query("Country in @selected_countries & Year == @year")
    df_mdi = df_mdi.query("Country in @selected_countries")
    dfp_year = dfp[dfp["Year"] == int(year)]

    #Get all cards inside the layout
    deployments_over_time_card = update_line_plot(dfp)
    sunburst_card = update_sunburst_plot(dfp_year)
    population_card = update_population_plot(df_deployment_capita)
    active_card = update_active_plot(df_active_personnel)
    deploy_meter_card = update_deployed_meter_plot(dfp_year, dfp)
    orgs_countries_card = update_total_deployment_plot(df_deployment_top_org)
    orgs_bar_card = update_orgs_bar_plot(dfp_year)
    mdi_card = update_mdi_plot(df_mdi)

    #If 2 countries use comparison meter plots
    if len(selected_countries) == 2:
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


# Top theatre deployment modal
@app.callback(
    Output("full-top-theatre-graph", "is_open"),
    [
        Input("expand_top-theatre", "n_clicks"),
        Input("expand-top-theatre-close", "n_clicks"),
    ],
    [State("full-top-theatre-graph", "is_open")],
)
def top_theatre_toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

