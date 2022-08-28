import pandas as pd
import numpy as np
from collections import Counter

from dash import Input, Output, State, exceptions
import plotly.express as px
import plotly.graph_objects as go

from .server import app
import mdi.constants as constants


# data
from old_app_2 import df, df_deployments, df_presence, mapbox_access_token


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
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="right",
        x=1,
        groupclick="toggleitem",
        itemsizing="constant",
    )

    hoverlabel = dict(font_size=16)

    mapbox = dict(
        accesstoken=mapbox_access_token,
        center=dict(lat=24, lon=0),
        zoom=1.5,
    )

    layout = dict(
        title="Military Deployments",
        hovermode="closest",
        height=1000,
        margin=go.layout.Margin(l=20, r=20, t=40, b=20),
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
    return figure

def _bar_plot(values, countries, max_value, percentage=False):
    fig = go.Figure(
        data=[go.Bar(y=countries, x=values, orientation='h', marker=dict(color='rgba(255, 0, 0, 0.8)'))])

    fig.add_trace(go.Bar(y=countries, x=[max_value - value for value in values], orientation='h',
                         marker=dict(color='rgb(58, 59, 60)')))
    fig.update_traces(width=0.2, hoverinfo='skip')
    fig.update(layout_showlegend=False)
    fig.update_layout(paper_bgcolor="rgb(0,0,0,0)", plot_bgcolor='rgba(0,0,0,0)', barmode='stack',
                      yaxis={'categoryorder':'array', 'categoryarray':countries},
                      font=dict(
                          size=20)
                      )
    fig.update_xaxes(showticklabels=False)

    annotations = []

    for value, country in zip(values, countries):
        value_str = str(value)
        if percentage:
            value_str = value_str + '%'

        annotations.append(dict(xref='x1', yref='y1',
                                y=country, x=max_value+max_value*0.03,
                                text=value_str,
                                font=dict(size=20),
                                showarrow=False))
    fig.update_layout(annotations=annotations)
    return fig


def percentage_calculate(n, d, scaling=1):
    try:
        number = (n/d) * scaling
        return round(number, 2)
    except ZeroDivisionError:
        return 0


def update_population_plot(df_deploy, df_population, year):
    df =  pd.DataFrame(columns=['Country Name', 'Deployment Per Capita'])

    for country in df_population["Country"].unique():
        total_deployed = df_deploy[df_deploy["Country"] == country]['Deployed'].sum()
        population = int(df_population[df_population["Country"] == country][year])
        country_name = df_population[df_population["Country"] == country]['Country Name'].values[0]

        df = pd.concat([df, pd.DataFrame([[country_name, percentage_calculate(total_deployed, population, 100000)]],
                                         columns=['Country Name', 'Deployment Per Capita'])])

    df = df.sort_values(by=['Deployment Per Capita'], ascending=False)
    deployment_mean = df["Deployment Per Capita"].mean()

    if df.shape[0] > 5:
        df = df.head(5)

    return _bar_plot(df['Deployment Per Capita'].iloc[::-1].values, df['Country Name'].iloc[::-1].values, 15), deployment_mean


def update_active_plot(df_deploy, df_active):
    df = pd.DataFrame(columns=['Country Name', 'Active Personnel'])

    for country in df_active["Country"].unique():
        total_deployed = df_deploy[df_deploy["Country"] == country]['Deployed'].sum()
        active_personnel = int(df_active[df_active["Country"] == country]['Personnel_Count'])
        country_name = df_active[df_active["Country"] == country]['Country Name'].values[0]

        df = pd.concat([df, pd.DataFrame([[country_name, percentage_calculate(total_deployed, active_personnel, 100)]],
                                         columns=['Country Name', 'Active Personnel'])])

    df = df.sort_values(by=['Active Personnel'], ascending=False)
    active_mean = df['Active Personnel'].mean

    if df.shape[0] > 5:
        df = df.head(5)

    return _bar_plot(df['Active Personnel'].iloc[::-1].values, df['Country Name'].iloc[::-1].values, 100, percentage=True), active_mean

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
    if selected_countries.value_counts()[True] == 1:
        return update_line_plot(dfp), update_pie_plot(dfp_year),
#               update_population_plot(dfp_year, df_population, str(year))[0], \
#               update_active_plot(dfp_year, df_active[df_active["Year"] == int(year)])[0]

    elif selected_countries.value_counts()[True] == 2:
        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)]),
#               update_population_plot(dfp_year, df_population, str(year))[0], \
#               update_active_plot(dfp_year, df_active[df_active["Year"] == int(year)])[0]

    else:
        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)]),
#               update_population_plot(dfp_year, df_population, str(year))[0], \
#               update_active_plot(dfp_year, df_active[df_active["Year"] == int(year)])[0]


@app.callback(
    Output(component_id="graph-line", component_property="figure"),
    Output(component_id="graph-sunburst", component_property="figure"),
#    Output(component_id="graph-population", component_property="figure"),
#    Output(component_id="graph-active", component_property="figure"),
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
