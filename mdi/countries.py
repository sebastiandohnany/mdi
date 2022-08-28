import pandas as pd
import numpy as np
from collections import Counter

from dash import Input, Output, State, exceptions
import plotly.express as px
import plotly.graph_objects as go

from .server import app
import mdi.constants as constants
from .plotting_functions import horizontal_bar_plot, percentage_calculate, summary_graph_card

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
    figure.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=340)
    return figure


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
    figure.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return figure


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
    #card = summary_graph_card(deployment_mean, "of deployed troops per 100,000 capita on average", fig)
    return {"fig":fig, "mean":str(deployment_mean)}


def update_active_plot(df_deploy, df_active):
    df = pd.DataFrame(columns=['Country Name', 'Active Personnel'])

    for country in df_active["Country"].unique():
        total_deployed = df_deploy[df_deploy["Country"] == country]['Deployed'].sum()
        active_personnel = int(df_active[df_active["Country"] == country]['Personnel_Count'])
        country_name = df_active[df_active["Country"] == country]['Country Name'].values[0]

        df = pd.concat([df, pd.DataFrame([[country_name, percentage_calculate(total_deployed, active_personnel, 100), total_deployed]],
                                         columns=['Country Name', 'Percent of Active Personnel', 'Total Deployed'])])

    df = df.sort_values(by=['Percent of Active Personnel'], ascending=False)
    active_mean = round((df['Percent of Active Personnel'].mean()),1)

    if df.shape[0] > 5:
        df = df.head(5)
        condensed = True
    else:
        condensed = False
    fig = horizontal_bar_plot(df['Percent of Active Personnel'].iloc[::-1].values,
                              df['Country Name'].iloc[::-1].values,
                              df['Percent of Active Personnel'].iloc[::-1].values,
                              100, percentage=True, condensed=condensed)
    #card = summary_graph_card(active_mean, "of available active duty personnel on average", fig)
    return {"fig":fig, "mean":str(active_mean)+"%"}

def update_deployed_meter_plot(df_deploy):
    df = df_deploy.groupby(["Theatre"])["Deployed"].sum()
    total_deployed = df_deploy["Deployed"].sum()
    highest_percentage = percentage_calculate(df.max(), total_deployed, scaling=100)
    fig = go.Figure(
        data=[go.Indicator(value=highest_percentage,
                           mode="gauge+number",
                           gauge={'axis': {'visible': False, 'range': [0, 100]},
                                  'bar': {'color': "rgba(255, 0, 0, 0.8)"},
                                  'bordercolor': "white",
                                  'steps': [
                                      {'range': [0, highest_percentage], 'color': 'rgba(255, 0, 0, 0.8)'},
                                      {'range': [highest_percentage, 100], 'color': 'rgb(58, 59, 60)'}]
                                  },
                           domain={'row': 0, 'column': 100},
                           number= {'suffix': "%", "font":{"size":30}})]
    )
    fig.update_layout(margin=dict(l=0, r=0, t=1, b=0),
                      height=150,)
    return {"fig":fig, 'theatre':df.idxmax()}

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

    if selected_countries.value_counts()[True] == 1:
        return update_line_plot(dfp), update_pie_plot(dfp_year), \
               population_data['fig'],population_data['mean'], \
               active_mean['fig'], active_mean['mean'],\
               deploy_meter['fig'], deploy_meter['theatre']

    elif selected_countries.value_counts()[True] == 2:
        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)]), \
               population_data['fig'],population_data['mean'], \
               active_mean['fig'], active_mean['mean'], \
               deploy_meter['fig'], deploy_meter['theatre']


    else:
        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)]),\
               population_data['fig'],population_data['mean'], \
               active_mean['fig'], active_mean['mean'], \
               deploy_meter['fig'], deploy_meter['theatre']


@app.callback(
    Output(component_id="graph-line", component_property="figure"),
    Output(component_id="graph-sunburst", component_property="figure"),
    Output(component_id="graph-population", component_property="figure"),
    Output(component_id="mean-population", component_property="children"),
    Output(component_id="graph-active", component_property="figure"),
    Output(component_id="mean-active", component_property="children"),
    Output(component_id="graph-theatre", component_property="figure"),
    Output(component_id="name-theatre", component_property="children"),
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
