# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

df = pd.read_excel('./data.xlsx')
df = df.dropna(subset=['Personnel'])

df['Size'] = [x*(100/df['Personnel'].max()) for x in df['Personnel']]


df1 = df.dropna(subset=['Year', 'Country', 'Organisation'])
df2 = df.dropna(subset=['Year', 'Country'])


def generate_table(dataframe, max_rows=30):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

figMap = px.scatter_geo(df1, locations="Theatre", color="Organisation", locationmode='country names',
                        hover_name="Country", size="Size", size_max=100, animation_frame="Year",
                        hover_data=['Theatre', 'Personnel', 'Country'],
                        width=1600, height=800,
                        projection="natural earth")

figMap2 = px.scatter_geo(df2, locations="Theatre", color="Country", locationmode='country names',
                        hover_name="Country", size="Size", size_max=100, animation_frame="Year",
                        hover_data=['Theatre', 'Personnel', 'Mission',
                                     'Country'],
                        width=1600, height=800,
                        projection="natural earth")

figMap.update_geos(
    resolution=50,
    showcoastlines=True, coastlinecolor="DarkGrey",
    showland=True, landcolor="LightYellow",
    showocean=True, oceancolor="Azure",
    showlakes=True, lakecolor="Azure",
    showrivers=True, rivercolor="Azure"
)

figMap2.update_geos(
    resolution=50,
    showcoastlines=True, coastlinecolor="DarkGrey",
    showland=True, landcolor="LightYellow",
    showocean=True, oceancolor="Azure",
    showlakes=True, lakecolor="Azure",
    showrivers=True, rivercolor="Azure"
)


app = Dash(__name__)

app.layout = html.Div([
    html.H4(children='Deployments'),

    dcc.Graph(
        id='map',
        figure=figMap
    ),

    dcc.Graph(
        id='map2',
        figure=figMap2
    ),

    # generate_table(df),
])

if __name__ == '__main__':
    app.run_server(debug=True)
