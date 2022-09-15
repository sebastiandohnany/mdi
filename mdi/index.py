import pandas as pd
from . import constants

from .app import df, df_deployments, df_presence, ROOT


def percentage_calculate(n, d, scaling=1):
    try:
        number = (n / d) * scaling
        return round(number, 1)
    except ZeroDivisionError:
        return 0


def calculate_mdi(df_deployments):
    year = "2021"

    # deployments
    all_countries = df_deployments["Country"].unique()

    # population
    df_population = pd.read_csv(ROOT + "data/MDVA_population.csv", delimiter=",")
    df_population = df_population.query("Country in @all_countries")

    # total deployed
    df_deployments = df_deployments[df_deployments["Year"] == int(year)]
    df_total_deployed = df_deployments.groupby(["Country"])["Deployed"].sum().to_frame()
    print(df_total_deployed)


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
