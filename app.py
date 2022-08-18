# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.exceptions import PreventUpdate


import constants

app = Dash(
    "Military Deployments Index",
    title="Military Deployments Index",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

mapbox_access_token = open(".mapbox_token").read()

# data
df = pd.read_excel("./data/MDVA_Deployments_LatLon.xlsx")

# country colors
df["Color"] = df["Country"].replace(to_replace=constants.country_colors)

# order
rank_by_country = (
    df.groupby(["Year", "Country"])["Deployed"].sum().sort_values(ascending=False)
)

# selection
selected_countries_default = pd.Series(
    data=dict.fromkeys(list(df.Country.unique()), True)
)
selected_year_default = pd.DataFrame(data={"year": [2014]})

# deployments and presence
df_deployments = df[df["MissionType"] == "Operation"]
df_presence = df[df["MissionType"] == "MillitaryPresence"]


def update_map(selected_year):
    # data
    def get_data(dfn, name):
        year = str(dfn.Year.iloc[0])
        order = rank_by_country.filter(like=year, axis=0)
        legendrank = order.index.droplevel("Year").get_loc(name)

        data = go.Scattermapbox(
            name=name,
            legendrank=legendrank,
            lat=dfn.Lat,
            lon=dfn.Lon,
            mode="markers",
            marker=go.scattermapbox.Marker(
                color=dfn.Color,
                opacity=0.6,
                # size=np.log2(dfp.Deployed, out=np.zeros_like(
                #     dfp.Deployed), where=(dfp.Deployed != 0)).values,
                size=dfn.Deployed,
                sizeref=30,
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

    legend = dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="right", x=1)

    hoverlabel = dict(font_size=16)

    layout = dict(
        title="Military Deployments",
        hovermode="closest",
        height=1000,
        font=dict(family=constants.theme["fontFamily"]),
        margin=go.layout.Margin(l=20, r=20, t=40, b=20),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center=dict(lat=24, lon=0),
            zoom=1.5,
        ),
        legend=legend,
        # updatemenus=[buttons],
        # sliders=[sliders],
        hoverlabel=hoverlabel,
    )

    # filter
    dfp = df_deployments[df_deployments["Year"] == selected_year]

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

    data = go.Sunburst(
        ids=list(dfm.Organisation.unique())
        + [x + y for x, y in zip(list(dfm.Organisation), list(dfm.MissionName))],
        labels=list(dfm.Organisation.unique()) + list(dfm.MissionName),
        parents=[""] * len(dfm.Organisation.unique()) + list(dfm.Organisation),
        values=list(dfo) + list(dfm.Deployed),
        branchvalues="total",
    )
    figure = go.Figure(data=data)
    return figure


def update_dashboard(selected_countries, year):
    dfp = df_deployments

    if selected_countries.value_counts()[True] == 1:
        countries = selected_countries[selected_countries == True].index
        dfp = dfp.query("Country in @countries")

        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)])

    elif selected_countries.value_counts()[True] == 2:
        countries = selected_countries[selected_countries == True].index
        dfp = dfp.query("Country in @countries")

        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)])

    else:
        countries = selected_countries[selected_countries == True].index
        dfp = dfp.query("Country in @countries")

        return update_line_plot(dfp), update_pie_plot(dfp[dfp["Year"] == int(year)])


# layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(
                        id="graph-map",
                        config={"displaylogo": False},
                        animate=True,
                        animation_options=dict(
                            frame={
                                "redraw": True,
                            },
                            transition={
                                "duration": 3000,
                                "ease": "cubic-in-out",
                            },
                        ),
                    ),
                ),
                dcc.Slider(
                    df_deployments["Year"].min(),
                    df_deployments["Year"].max(),
                    step=None,
                    value=df_deployments["Year"].min(),
                    marks={
                        str(year): str(year) for year in df_deployments["Year"].unique()
                    },
                    id="year-slider",
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

# callbacks


@app.callback(
    Output(component_id="graph-line", component_property="figure"),
    Output(component_id="graph-sunburst", component_property="figure"),
    Output(component_id="selected-countries", component_property="data"),
    Input(component_id="graph-map", component_property="restyleData"),
    Input(component_id="selected-countries", component_property="data"),
    Input(component_id="selected-year", component_property="data"),
)
def new_country_selection(selection_changes, selected_countries, selected_year):
    if selected_countries is None:
        selected_countries = selected_countries_default
    else:
        selected_countries = pd.read_json(selected_countries, typ="series")

    if selected_year is None:
        selected_year = selected_year_default
        actual_year = selected_year["year"].iloc[0]
    else:
        selected_year = pd.read_json(selected_year, typ="frame")
        actual_year = selected_year["year"].iloc[0]

    if selection_changes is not None:
        selected_countries.iloc[selection_changes[1]] = list(
            map(lambda x: True if x == True else False, selection_changes[0]["visible"])
        )
    return (
        *update_dashboard(selected_countries, actual_year),
        selected_countries.to_json(),
    )


@app.callback(
    Output(component_id="graph-map", component_property="figure"),
    Output(component_id="selected-year", component_property="data"),
    Input(component_id="graph-map", component_property="figure"),
    Input(component_id="year-slider", component_property="value"),
)
def update_year(figure, actual_year):
    figure = update_map(actual_year)
    figure.update_layout()
    selected_year = selected_year_default
    selected_year["year"].iloc[0] = actual_year
    return figure, selected_year.to_json()


# run
if __name__ == "__main__":
    app.run_server(debug=True)
