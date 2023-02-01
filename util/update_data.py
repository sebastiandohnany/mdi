import pandas as pd

from mdi.plotting_functions import percentage_calculate
from mdi import constants
from mdi.index import calculate_mdi
from mdi.app import ROOT

class UpdateData:
    def __init__(self):
        # Load data from files
        df_deploy_full = pd.read_excel(ROOT + "data/MDVA_Deployments_LatLon.xlsx")
        self.df_active = pd.read_excel(ROOT + "data/MDVA_ActiveDuty.xlsx")
        self.df_population = pd.read_csv(ROOT + "data/MDVA_Population.csv", delimiter=",")

        # Query deployments and presence
        self.df_deployments = df_deploy_full[df_deploy_full["MissionType"] == "Operation"]
        self.df_presence = df_deploy_full[df_deploy_full["MissionType"] == "MilitaryPresence"]

    def calculate_per_capita(self):
        df_deploy = self.df_deployments
        df_population = self.df_population
        df = pd.DataFrame(columns=["Country", "Country Name", "Year", "Deployment Per Capita"])

        for year in df_deploy["Year"].unique():
        # Calculate deployment per 100,000 capita for each country
            for country in df_deploy["Country"].unique():
                total_deployed = df_deploy.query("Country == @country & Year == @year")["Deployed"].sum()

                population = int(df_population.query("Country == @country")[str(year)])
                country_name = constants.country_codes[country]

                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [
                                [
                                    country,
                                    country_name,
                                    year,
                                    percentage_calculate(total_deployed, population, 100000),
                                ]
                            ],
                            columns=["Country", "Country Name", "Year", "Deployment Per Capita"],
                        ),
                    ]
                )
        df.to_csv(ROOT + 'data/deployment_per_capita.csv', index=False)
        print("Saved deployment per capita data to deployment_per_capita.csv")
        return None

    def calculate_mdi(self):
        df_deployments = self.df_deployments
        mdi = None
        for year in df_deployments["Year"].unique():
            df = calculate_mdi(df_deployments, year)
            df["Year"] = year
            if mdi is None:
                mdi = df
            else:
                mdi = pd.concat([mdi, df])
        mdi.to_csv(ROOT + 'data/mdi.csv', index=False)
        print("Saved mdi data to mdi.csv")

        return None


    def calculate_active_personnel(self):
        df_deploy = self.df_deployments
        df_active = self.df_active
        df = pd.DataFrame(columns=["Country", "Country Name", "Year", "Percent of Active Personnel", "Total Deployed"])

        for year in df_deploy["Year"].unique():
            for country in df_deploy["Country"].unique():
                total_deployed = df_deploy.query("Country == @country & Year == @year")["Deployed"].sum()
                active_personnel = int( df_active.query("Country == @country & Year == @year")["Personnel_Count"])
                country_name = constants.country_codes[country]

                df = pd.concat(
                    [
                        df,
                        pd.DataFrame(
                            [
                                [
                                    country,
                                    country_name,
                                    year,
                                    percentage_calculate(total_deployed, active_personnel, 100),
                                    total_deployed,
                                ]
                            ],
                            columns=[
                                "Country",
                                "Country Name",
                                "Year",
                                "Percent of Active Personnel",
                                "Total Deployed",
                            ],
                        ),
                    ]
                )

        df.to_csv(ROOT + 'data/active_personnel.csv', index=False)
        print("Saved active personnel data to active_personnel.csv")

    def calculate_organisation_breakdown(self):
        df_deploy = self.df_deployments

        df = pd.DataFrame(columns=["Country", "Year", "Organisation", "Deployed", "Percentage of Total Deployment"])

        for year in df_deploy["Year"].unique():
            for country in df_deploy["Country"].unique():
                df_country = df_deploy.query("Country == @country & Year == @year")
                country_sum = df_country["Deployed"].sum()

                df_country = df_country.groupby(['Country', 'Organisation', "Year"])['Deployed'].sum().reset_index()

                def _calc_total_deploy_percentage(row):
                    percentage = percentage_calculate(
                        row["Deployed"],
                        country_sum,
                        scaling=100,
                    )
                    return percentage

                df_country["Percentage of Total Deployment"] = df_country.apply(
                    _calc_total_deploy_percentage, axis=1
                )

                df = pd.concat([df, df_country.loc[:, ["Country", "Year", "Organisation", "Deployed", "Percentage of Total Deployment"]]])

        df.to_csv(ROOT + 'data/top_organisations.csv', index=False)
        print("Saved top organisations data to top_organisations.csv")

if __name__ == "__main__":
    update = UpdateData()
    update.calculate_per_capita()
    update.calculate_mdi()
    update.calculate_active_personnel()
    update.calculate_organisation_breakdown()
    print("Finishes updating")