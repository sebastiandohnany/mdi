import pandas as pd
import plotly as pl
from . import constants
import plotly.express as px
import plotly as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import scipy.stats as sts

from .app import df, df_deployments, df_presence, ROOT


def percentage_calculate(n, d, scaling=1):
    try:
        number = (n / d) * scaling
        return round(number, 1)
    except ZeroDivisionError:
        return 0


def combined_z_scores(z1, z2, w1, w2):
    return ((w1 / (w1 + w2)) * z1 + (w2 / (w1 + w2)) * z2) / np.sqrt(
        np.power(w1 / (w1 + w2), 2) + np.power(w2 / (w1 + w2), 2)
    )


def calculate_mdi(df_deployments):
    year = "2014"

    df_deployments.sort_values(by="Country", inplace=True)

    all_countries = df_deployments["Country"].unique()
    df_statistics = pd.DataFrame({"Country": all_countries})

    # population
    df_population = pd.read_csv(ROOT + "data/MDVA_population.csv", delimiter=",")
    df_population = df_population.query("Country in @all_countries")

    # total deployed
    df_deployments = df_deployments[df_deployments["Year"] == int(year)]
    total_deployments = df_deployments.groupby(["Country"])["Deployed"].sum().to_list()
    df_statistics["Total"] = total_deployments
    print(df_statistics)

    # per capita deployment
    deployments_per_capita = []
    deployments_per_many_capita = []
    population = []
    for country in all_countries:
        total_deployed = int(
            df_statistics[df_statistics["Country"] == country]["Total"]
        )

        pop = int(df_population[df_population["Country"] == country][year])
        population.append(pop)

        per_capita = total_deployed / pop
        deployments_per_capita.append(per_capita)

        per_many_capita = percentage_calculate(total_deployed, pop, 100000)
        deployments_per_many_capita.append(per_many_capita)

    df_statistics["PerCapita"] = deployments_per_capita
    df_statistics["PerManyCapita"] = deployments_per_many_capita
    df_statistics["Population"] = population
    print(df_statistics)

    # multiply total and per capita, normalise 0-10
    multiply = []
    for country in all_countries:
        total_deployed = int(
            df_statistics[df_statistics["Country"] == country]["Total"]
        )
        per_capita = float(
            df_statistics[df_statistics["Country"] == country]["PerCapita"]
        )
        calc = total_deployed * per_capita
        multiply.append(calc)

    multiply_min = min(multiply)
    multiply_max = max(multiply) - multiply_min
    divisor = multiply_max / 5
    for i in range(len(multiply)):
        multiply[i] = (multiply[i] - multiply_min) / divisor

    df_statistics["Multiply"] = multiply

    # # normalise both to 0-1
    # total_norm = []
    # total_min = min(total_deployments)
    # total_max = max(total_deployments) - total_min
    # divisor_total = total_max / 1
    # for i in range(len(total_deployments)):
    #     total_norm.append((total_deployments[i] - total_min) / divisor_total)
    # df_statistics["Total Norm"] = total_norm

    # pop_norm = []
    # pop_min = min(population)
    # pop_max = max(population) - pop_min
    # divisor_pop = pop_max / 1
    # for i in range(len(population)):
    #     pop_norm.append((population[i] - pop_min) / divisor_pop)
    # df_statistics["Population Norm"] = pop_norm

    # z-scores
    pop_z = sts.zscore(population)
    total_z = sts.zscore(total_deployments)

    df_statistics["Population z"] = pop_z
    df_statistics["Total z"] = total_z

    avg_index = np.mean(np.array([-pop_z, total_z]), axis=0)

    df_statistics["Avg index"] = avg_index

    # z-scores with per capita
    percapita_z = sts.zscore(deployments_per_capita)
    df_statistics["Per capita z"] = percapita_z

    zavg_index_percapita_total = combined_z_scores(
        np.array(percapita_z), np.array(total_z), 0.5, 0.5
    )
    zavg_index_percapita_total_p = combined_z_scores(
        np.array(percapita_z), np.array(total_z), 0.4, 0.6
    )
    print(zavg_index_percapita_total_p)
    df_statistics["Avg z per capita"] = zavg_index_percapita_total

    print(df_statistics)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df_statistics["Country"],
            y=df_statistics["Total"],
            name="total deplyoments",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df_statistics["Country"],
            y=df_statistics["PerManyCapita"],
            name="per capita",
        ),
        secondary_y=True,
    )

    # fig.add_trace(
    #     go.Bar(
    #         x=df_statistics["Country"],
    #         y=df_statistics["Multiply"],
    #         name="multiply index",
    #         offsetgroup=3,
    #     ),
    #     secondary_y=True,
    # )

    # corr = np.corrcoef(
    #     np.array(df_statistics["Total"]), np.array(df_statistics["Multiply"])
    # )

    # fig.update_layout(
    #     title="Year: " + year + " Corr of index and total: " + str(corr[0, 1])
    # )

    # r1 = np.arange(0, 1, 0.05)
    # r2 = np.arange(0, 1, 0.05)

    # r3 = []
    # for v1, v2 in zip(r1, r2):
    #     r3.append(v1 * v2)

    # fig = make_subplots()

    fig.add_trace(
        go.Scatter(y=multiply, x=all_countries, name="Multiply"),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(y=avg_index, x=all_countries, name="Avg index"), secondary_y=True
    )

    fig.add_trace(
        go.Scatter(
            y=zavg_index_percapita_total, x=all_countries, name="Per capita index"
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            y=zavg_index_percapita_total_p,
            x=all_countries,
            name="Per capita index weighted avg",
        ),
        secondary_y=True,
    )

    fig.show()


# # Calculate deployment per 100,000 capita for each country
# df_per_capita = pd.DataFrame(columns=["Country", "Deployment Per Capita"])
# for country in df_population["Country"].unique():
#     total_deployed = df_deploy[df_deploy["Country"] == country]["Deployed"].sum()
#     population = int(df_population[df_population["Country"] == country][year])
#     print(total_deployed)
#     print(population)
#     # country_name = constants.country_codes[country]

#     df_per_capita = pd.concat(
#         [
#             df_per_capita,
#             pd.DataFrame(
#                 [
#                     [
#                         country,
#                         percentage_calculate(total_deployed, population, 100000),
#                     ]
#                 ],
#                 columns=["Country", "Deployment Per Capita"],
#             ),
#         ]
#     )

# df_per_capita = df_per_capita.sort_values(by=["Deployment Per Capita"], ascending=False)


# print(df_total_deployed)
# print(df_per_capita)


# mdi = pd.DataFrame(columns=["Country", "MDI"])
# for country in df_per_capita["Country"].unique():
#     td = df_total_deployed[country]
#     pc = df_per_capita[df_per_capita["Country"] == country][
#         "Deployment Per Capita"
#     ].iloc[0]

#     print(td)
#     print(pc)

#     mdi_temp = td * pc
#     print(mdi_temp)

#     mdi = pd.concat(
#         [
#             mdi,
#             pd.DataFrame(
#                 [[country, mdi_temp]],
#                 columns=["Country", "MDI"],
#             ),
#         ]
#     )

# print(mdi)
