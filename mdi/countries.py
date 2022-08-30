import pandas as pd
import numpy as np
from collections import Counter

from dash import Input, Output, State, exceptions
import plotly.express as px
import plotly.graph_objects as go

from .server import app
import mdi.constants as constants
from .plotting_functions import horizontal_bar_plot, percentage_calculate, summary_graph_card, meter_plot, \
    country_orgs_bar_plot

# data
from .app import df, df_deployments, df_presence, mapbox_access_token

# default store
selected_countries_default = pd.Series(
    data=dict.fromkeys(
        list(df_deployments.sort_values(by="Country").Country.unique()), True
    )
)
selected_year_default = pd.DataFrame(data={"year": [2021]})

# rank
rank_countries_by_deployed = (
    df_deployments.groupby(["Country"])["Deployed"].sum().sort_values(ascending=False)
)


def update_map(selected_year):
    def get_data(dfn, name):
        data = go.Scattermapbox(
            name=name,
            legendrank=rank_countries_by_deployed.index.get_loc(name),
            legendgroup=constants.country_regions.get(name, "N/A"),
            legendgrouptitle_text=constants.country_regions.get(name, "N/A"),
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
            + "Deployed: %{customdata[9]} <br>"
            + "Organisation: %{customdata[6]} <br>"
            + "Mission Name: %{customdata[7]} <br>"
            + "Mission Type: %{customdata[8]} <br>"
            + "<extra></extra>",
            showlegend=True,
        )
        return data

    # # customise
    # sliders = dict(
    #     active=0,
    #     yanchor="top",
    #     xanchor="left",
    #     currentvalue={
    #         "font": {"size": 20},
    #         "prefix": "Year:",
    #         "visible": True,
    #         "xanchor": "right",
    #     },
    #     transition={"duration": 300, "easing": "cubic-in-out"},
    #     pad={"b": 10, "t": 50},
    #     len=0.9,
    #     x=0.1,
    #     y=0,
    #     steps=[
    #         {
    #             "args": [
    #                 [str(year)],
    #                 {
    #                     "frame": {"duration": 300},
    #                     "mode": "immediate",
    #                     "transition": {"duration": 0},
    #                 },
    #             ],
    #             "label": str(year),
    #             "method": "animate",
    #         }
    #         for year in np.sort(df["Year"].unique())
    #     ],
    # )

    # buttons = dict(
    #     buttons=[
    #         {
    #             "args": [
    #                 None,
    #                 {
    #                     "frame": {"duration": 500},
    #                     "fromcurrent": True,
    #                     "transition": {"duration": 300, "easing": "quadratic-in-out"},
    #                 },
    #             ],
    #             "label": "Play",
    #             "method": "animate",
    #         },
    #         {
    #             "args": [
    #                 [None],
    #                 {
    #                     "frame": {"duration": 0},
    #                     "mode": "immediate",
    #                     "transition": {"duration": 0},
    #                 },
    #             ],
    #             "label": "Pause",
    #             "method": "animate",
    #         },
    #     ],
    #     direction="left",
    #     pad={"r": 10, "t": 87},
    #     showactive=False,
    #     type="buttons",
    #     x=0.1,
    #     xanchor="right",
    #     y=0,
    #     yanchor="top",
    # )

    legend = dict(
        # orientation="h",
        # yanchor="right",
        # y=-0.3,
        # xanchor="right",
        # x=1,
        groupclick="toggleitem",
        itemsizing="constant",
    )

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
        height=800,
        margin=go.layout.Margin(l=0, r=0, t=0, b=0),
        mapbox=mapbox,
        legend=legend,
        hoverlabel=hoverlabel,
        # updatemenus=[buttons],
        # sliders=[sliders],
        font=dict(family=constants.theme["fontFamily"]),
        uirevision="perservere",
        paper_bgcolor="rgb(0,0,0,0)",
        plot_bgcolor='rgba(0,0,0,0)',
    )

    # filter and sort
    dfp = df_deployments[df_deployments["Year"] == selected_year].sort_values(
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
    # frames = [
    #     go.Frame(
    #         data=[
    #             get_data(
    #                 dfp.loc[(dfp["Country"] == country) & (dfp["Year"] == year)],
    #                 country,
    #             )
    #             for country in dfp["Country"].unique()
    #         ],
    #         name=str(year),
    #     )
    #     for year in np.sort(dfp["Year"].unique())
    # ]

    figure = go.Figure(
        data=data,
        # frames=frames,
        layout=layout,
    )

    figure.update_layout(legend=dict(bgcolor='rgba(0,0,0,0)'))
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
        )
        return data

    data = [
        get_data(dfp[dfp["Country"] == country], country)
        for country in dfp["Country"].unique()
    ]
    figure = go.Figure(data=data)
    figure.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=340, paper_bgcolor="rgb(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)')

    card = summary_graph_card("Deployments over time", "", figure, title_colour='black')

    return card


def update_pie_plot(dfp):
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
    )
    figure = go.Figure(data=data)
    figure.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgb(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)')

    card = summary_graph_card("Distribution between organisations and missions", "", figure, title_colour="black")

    return card


def update_population_plot(df_deploy, df_population, year):
    df= pd.DataFrame(columns=['Country Name', 'Deployment Per Capita'])

    for country in df_population["Country"].unique():
        total_deployed = df_deploy[df_deploy["Country"] == country]['Deployed'].sum()
        population = int(df_population[df_population["Country"] == country][year])
        country_name = df_population[df_population["Country"] == country]['Country Name'].values[0]

        df = pd.concat([df, pd.DataFrame([[country_name, percentage_calculate(total_deployed, population, 100000)]],
                                         columns=['Country Name', 'Deployment Per Capita'])])

    df = df.sort_values(by=['Deployment Per Capita'], ascending=False)
    deployment_mean = round(df["Deployment Per Capita"].mean(), 1)

    if df.shape[0] > 5:
        df = df.head(5)
        condensed=True
    else:
        condensed = False
    fig = horizontal_bar_plot(df['Deployment Per Capita'].iloc[::-1].values,
                              df['Country Name'].iloc[::-1].values,
                              df['Deployment Per Capita'].iloc[::-1].values, 15, condensed=condensed)
    card = summary_graph_card(deployment_mean, "of deployed troops per 100,000 capita on average", fig,
                              title_colour='rgba(255, 0, 0, 0.8)')
    return card


def update_active_plot(df_deploy, df_active):
    df = pd.DataFrame(columns=['Country Name', 'Active Personnel'])

    for country in df_active["Country"].unique():
        total_deployed = df_deploy[df_deploy["Country"] == country]['Deployed'].sum()
        active_personnel = int(df_active[df_active["Country"] == country]['Personnel_Count'])
        country_name = df_active[df_active["Country"] == country]['Country Name'].values[0]

        df = pd.concat([df, pd.DataFrame([[country_name, percentage_calculate(total_deployed, active_personnel, 100), total_deployed]],
                                         columns=['Country Name', 'Percent of Active Personnel', 'Total Deployed'])])

    df = df.sort_values(by=['Percent of Active Personnel'], ascending=False)
    active_mean = round((df['Percent of Active Personnel'].mean()), 1)

    if df.shape[0] > 5:
        df = df.head(5)
        condensed = True
    else:
        condensed = False
    fig = horizontal_bar_plot(df['Percent of Active Personnel'].iloc[::-1].values,
                              df['Country Name'].iloc[::-1].values,
                              df['Percent of Active Personnel'].iloc[::-1].values,
                              100, percentage=True, condensed=condensed)

    card = summary_graph_card(str(active_mean)+"%", "of available active duty personnel on average", fig,
                              title_colour='rgba(255, 0, 0, 0.8)')
    return card

def update_deployed_meter_plot(df_deploy):
    df = df_deploy.groupby(["Theatre"])["Deployed"].sum()
    total_deployed = df_deploy["Deployed"].sum()

    #Theatre with highest percentage deployment
    highest_percentage = percentage_calculate(df.max(), total_deployed, scaling=100)

    #Make figure and card
    fig = meter_plot(highest_percentage, {'min':0, 'max':100})
    card = summary_graph_card(df.idxmax(), "top deployment theatre", fig, title_colour='rgba(255, 0, 0, 0.8)')

    return card


def update_total_deployment_plot(df_deploy):
    df = df_deploy.copy()
    condensed = False

    # select top 5 deployment countries
    if len(df_deploy["Country"].unique()) > 5:
            country_sum = df_deploy.groupby(["Country"])["Deployed"].sum().sort_values(ascending=False)
            country_list= list(country_sum.head(5).index)
            df = df.query("Country in @country_list")
            condensed = True

    #query top 5 organisations to include in the graph
    top_orgs = list(df.groupby(['Organisation']).sum().sort_values(by='Deployed', ascending=False).head(5).index)

    #Rename all other orgs to "Other" and sum
    df.loc[~df['Organisation'].isin(top_orgs), 'Organisation'] = "Other"
    df = df.groupby(["Country", "Organisation"])["Deployed"].sum().reset_index().sort_values(by="Organisation")


    #Make figure and card
    fig = country_orgs_bar_plot(df, condensed=condensed)
    card = summary_graph_card("Total deployed personnel", "per country by different organisations", fig,
                              title_colour='rgba(255, 0, 0, 0.8)')
    return card

def update_orgs_bar_plot(df_deploy):
    df = df_deploy.copy()
    total_deployed = df_deploy["Deployed"].sum()

    # query top 5 organisations, rest goes under other
    top_orgs = df.groupby(['Organisation']).sum().sort_values(by='Deployed', ascending=False).head(5)
    other_orgs = total_deployed - top_orgs['Deployed'].sum()
    deployed_numbers = list(top_orgs['Deployed'])
    deployed_numbers.append(other_orgs)

    deployment_percentage = [percentage_calculate(number, total_deployed, 100) for number in deployed_numbers]

    deployed_names_orgs = list(top_orgs.index)
    deployed_names_orgs.append("Other")

    colours = [constants.organisation_colors.get(
                    org,
                    constants.country_colors.get(
                        org, constants.organisation_colors.get("default"))) for org in deployed_names_orgs]

    fig = horizontal_bar_plot(deployment_percentage[::-1], deployed_names_orgs[::-1], deployment_percentage[::-1], max_value=100,
                              percentage=True, colour=colours[::-1])
    card = summary_graph_card(total_deployed, "total troop deployment", fig, title_colour='rgba(255, 0, 0, 0.8)')
    return card



def update_dashboard(selected_countries, year):
    dfp = df_deployments
    df_active = pd.read_excel("./temp/MDVA_active-duty.xlsx")
    df_population = pd.read_csv("./temp/MDVA_population.csv", delimiter=',')

    if True not in selected_countries.values:
        raise exceptions.PreventUpdate

    countries = selected_countries[selected_countries == True].index
    dfp = dfp.query("Country in @countries")
    df_active = df_active.query("Country in @countries")
    df_population = df_population.query("Country in @countries")
    # TODO: maybe unnecessary to choose which one

    dfp_year = dfp[dfp["Year"] == int(year)]

    population_data = update_population_plot(dfp_year, df_population, str(year))
    active_mean = update_active_plot(dfp_year, df_active[df_active["Year"] == int(year)])
    deploy_meter = update_deployed_meter_plot(dfp_year)
    orgs_data = update_total_deployment_plot(dfp_year)
    orgs_bar = update_orgs_bar_plot(dfp_year)

    if selected_countries.value_counts()[True] == 1:
        return update_line_plot(dfp), update_pie_plot(dfp_year), \
               population_data, active_mean, deploy_meter, orgs_data, orgs_bar

    elif selected_countries.value_counts()[True] == 2:
        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)]), \
               population_data, active_mean, deploy_meter, orgs_data, orgs_bar


    else:
        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)]),\
               population_data, active_mean, deploy_meter, orgs_data, orgs_bar


@app.callback(
    Output(component_id="card-line", component_property="children"),
    Output(component_id="card-sunburst", component_property="children"),
    Output(component_id="card-population", component_property="children"),
    Output(component_id="card-active", component_property="children"),
    Output(component_id="card-theatre", component_property="children"),
    Output(component_id="card-countries-orgs", component_property="children"),
    Output(component_id="card-bar-orgs", component_property="children"),
    Input(component_id="selected-countries", component_property="data"),
    Input(component_id="selected-year", component_property="data"),
)
def reload_dashboard(selected_countries, selected_year):
    selected_year = selected_year_default
    actual_year = selected_year["year"].iloc[0]

    selected_countries = pd.read_json(selected_countries, typ="series")

    return update_dashboard(selected_countries, actual_year)


@app.callback(
    Output(component_id="selected-countries", component_property="data"),
    Input(component_id="graph-map", component_property="restyleData"),
    Input(component_id="selected-countries", component_property="data"),
)
def update_selected_countries(selection_changes, selected_countries):
    if selected_countries is None:
        selected_countries = selected_countries_default
    else:
        selected_countries = pd.read_json(selected_countries, typ="series")

    if selection_changes is not None:
        selected_countries.iloc[selection_changes[1]] = list(
            map(
                lambda x: True if x == True else False,
                selection_changes[0].get("visible"),
            )
        )

    return selected_countries.to_json()


@app.callback(
    Output(component_id="selected-year", component_property="data"),
    Output(component_id="graph-map", component_property="figure"),
    Input(component_id="year-slider", component_property="value"),
    State(component_id="graph-map", component_property="relayoutData"),
)
def update_selected_year(actual_year, data):
    zoom = 1.5
    center = dict(lat=24, lon=0)
    if data:
        zoom = data.get("mapbox.zoom", 1.5)
        center = data.get("mapbox.center", dict(lat=24, lon=0))

    figure = update_map(actual_year)
    figure.update_layout(mapbox_zoom=zoom, mapbox_center=center)

    selected_year = selected_year_default
    selected_year["year"].iloc[0] = actual_year

    return selected_year.to_json(), figure
