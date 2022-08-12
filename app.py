# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


import constants

app = Dash("Military Deployments", title="Military Deployments")

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
selected_countries = pd.Series(data=dict.fromkeys(list(df.Country.unique()), True))


def update_map():
    dfp = df[df["Mission Type"] == "Operation"]

    def get_data(dfn):
        year = str(dfn.Year.iloc[0])
        name = dfn.Country.iloc[0]
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
            # hovertext=[
            #     f'{row.Deployed}<br>{row.Country}<br>{row.Organisation}<br>{row["Mission Name"]}'
            #     for i, row in dfn.iterrows()
            # ],
            # hoverinfo=["text", "name"],
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

    sliders = dict(
        active=0,
        yanchor="top",
        xanchor="left",
        currentvalue={
            "font": {"size": 20},
            "prefix": "Year:",
            "visible": True,
            "xanchor": "right",
        },
        transition={"duration": 300, "easing": "cubic-in-out"},
        pad={"b": 10, "t": 50},
        len=0.9,
        x=0.1,
        y=0,
        steps=[
            {
                "args": [
                    [str(year)],
                    {
                        "frame": {"duration": 300},
                        "mode": "immediate",
                        "transition": {"duration": 0},
                    },
                ],
                "label": str(year),
                "method": "animate",
            }
            for year in np.sort(df["Year"].unique())
        ],
    )

    buttons = dict(
        buttons=[
            {
                "args": [
                    None,
                    {
                        "frame": {"duration": 500},
                        "fromcurrent": True,
                        "transition": {"duration": 300, "easing": "quadratic-in-out"},
                    },
                ],
                "label": "Play",
                "method": "animate",
            },
            {
                "args": [
                    [None],
                    {
                        "frame": {"duration": 0},
                        "mode": "immediate",
                        "transition": {"duration": 0},
                    },
                ],
                "label": "Pause",
                "method": "animate",
            },
        ],
        direction="left",
        pad={"r": 10, "t": 87},
        showactive=False,
        type="buttons",
        x=0.1,
        xanchor="right",
        y=0,
        yanchor="top",
    )

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
        updatemenus=[buttons],
        sliders=[sliders],
        hoverlabel=hoverlabel,
    )

    data = [
        get_data(
            dfp.loc[
                (dfp["Country"] == country)
                & (dfp["Year"] == np.sort(dfp["Year"].unique())[0])
            ]
        )
        for country in dfp["Country"].unique()
    ]
    frames = [
        go.Frame(
            data=[
                get_data(dfp.loc[(dfp["Country"] == country) & (dfp["Year"] == year)])
                for country in dfp["Country"].unique()
            ],
            name=str(year),
        )
        for year in np.sort(dfp["Year"].unique())
    ]

    figure = go.Figure(data=data, frames=frames, layout=layout)

    return figure


def update_dashboard(selected_countries):
    dfp = df

    if selected_countries.value_counts()[True] == 1:
        country = selected_countries[selected_countries == True].index[0]
        dfp = dfp[dfp.Country == country]

        dfp = dfp.groupby(["Year"])["Deployed"].sum()
        print(dfp)

        data = go.Scatter(x=dfp.index, y=dfp.values)

        figure = go.Figure(data=data)
        return figure

    elif selected_countries.value_counts()[True] == 2:
        pass

    else:
        data = go.Scatter(x=[1, 2, 3], y=[10, 12, 14])

        figure = go.Figure(data=data)
        return figure


# layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(
                        id="graph-map",
                        figure=update_map(),
                    )
                ),
            ],
        ),
        html.P(id="selected-countries"),
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(
                        id="graph-trend",
                    )
                ),
            ],
        ),
    ],
    style={"fontFamily": constants.theme["fontFamily"]},
)

# callbacks


@app.callback(
    Output(component_id="selected-countries", component_property="children"),
    Output(component_id="graph-trend", component_property="figure"),
    Input(component_id="graph-map", component_property="restyleData"),
)
def new_country_selection(selection_changes):
    if selection_changes is not None:
        selected_countries.iloc[selection_changes[1]] = list(
            map(lambda x: True if x == True else False, selection_changes[0]["visible"])
        )
    return (
        f"Selected countries: {selected_countries} and changes: {selection_changes}",
        update_dashboard(selected_countries),
    )


# run
if __name__ == "__main__":
    app.run_server(debug=True)
