import pandas as pd
import plotly as pl
from . import constants
import plotly.express as px
import plotly as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import scipy.stats as sts

from .app import ROOT


def combined_z_scores(z1, z2, w1, w2):
    return ((w1 / (w1 + w2)) * z1 + (w2 / (w1 + w2)) * z2) / np.sqrt(
        np.power(w1 / (w1 + w2), 2) + np.power(w2 / (w1 + w2), 2)
    )


def rescale(values, new_min=0, new_max=100):
    output = []
    old_min, old_max = min(values), max(values)

    for v in values:
        new_v = (new_max - new_min) / (old_max - old_min) * (v - old_min) + new_min
        output.append(new_v)

    return output


def calculate_mdi(df_deployments, year):
    year = str(year)
    df_deployments = df_deployments.sort_values(by="Country")

    all_countries = df_deployments["Country"].unique()
    df_statistics = pd.DataFrame({"Country": all_countries})

    # population
    df_population = pd.read_csv(ROOT + "data/MDVA_Population.csv", delimiter=",")
    df_population = df_population.query("Country in @all_countries")

    # total deployed
    df_deployments = df_deployments[df_deployments["Year"] == int(year)]
    total_deployments = df_deployments.groupby(["Country"])["Deployed"].sum().to_list()
    df_statistics["Total"] = total_deployments

    # per capita deployment
    deployments_per_capita = []
    population = []
    for country in all_countries:
        total_deployed = int(
            df_statistics[df_statistics["Country"] == country]["Total"]
        )

        pop = int(df_population[df_population["Country"] == country][year])
        population.append(pop)

        per_capita = total_deployed / pop
        deployments_per_capita.append(per_capita)

    df_statistics["PerCapita"] = deployments_per_capita
    df_statistics["Population"] = population

    # z-scores
    total_z = sts.zscore(total_deployments)
    df_statistics["Total-Z"] = total_z

    percapita_z = sts.zscore(deployments_per_capita)
    df_statistics["PerCapita-Z"] = percapita_z

    # combined_z_total_percapita = combined_z_scores(
    #     np.array(percapita_z), np.array(total_z), 1, 1
    # )

    combined_z_total_percapita = np.array(percapita_z) + np.array(total_z)
    df_statistics["Combined-Z_Total_PerCapita"] = combined_z_total_percapita

    # mdi = sts.norm.cdf(combined_z_total_percapita) * 2.5
    mdi = np.round(rescale(combined_z_total_percapita, 0, 100), 0).astype(int)
    df_statistics["MDI"] = mdi

    return df_statistics
