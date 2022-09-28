# Methodology

**Suggested citation:** Massie, J., Tallová, B., Dohnány, S., Bajnoková, N., (2022) *Military Deployment Index*. Network for Strategic Analysis. Available at: [www.mdi.ras-nsa.ca](http://www.mdi.ras-nsa.ca/).

**Project leader:** Justin Massie

**Conceptualisation and design:** Barbora Tallová

**Developers:** Sebastián Dohnány, Natália Bajnoková

**Source of data:** The Military Balance, International Institute for Strategic Studies

**Data inquiries:** [info@ras-nsa.ca](mailto:info@ras-nsa.ca)

**Source code openly available at** [github.com/sebastiandohnany/mdi](https://github.com/sebastiandohnany/mdi) under MIT License (2022).


  

## Explanatory Notes

Our project seeks to measure and visualize troop deployments across the globe. At the initial stage, it offers two main contributions. First, it introduces the Military Deployment Index, a new measure of military deployability based on a balanced composition of absolute deployment figures and values adjusted to population. Second, it provides a nuanced empirical mapping of the global military power by tracking deployment distributions of troops across space, command structures and operations. Developed using reliable sources and careful data processing, our tools are designed to assist an accurate and standardized study of troop deployments.

  

However, there are certain limits to our data. Although we tested for inaccuracies and treated where possible, those inherent to our sources and their means of data collection remain present. The figures you see here may thus differ from deployment figures published elsewhere, namely by individual governments. Our measures and visualizations are dependent on the data provided by national governments to the International Institute for Strategic Studies. While it is not feasible to verify each observation against alternative national sources, our statistics benefit from being based on a single source, rendering them suitable for cross-country analysis.

  

## The Military Deployment Index

  

The Military Deployment Index is calculated for each country on an annual basis. It is composed of Z-scores for absolute troop deployments and deployments per population. Although related, the correlation between our variables does not exceed .37 in any given year. The sum of the respective Z-scores is scaled from 0 to 100, creating a single measure of deployability that takes into account both the absolute and per capita troop deployments.
  

## Data and Rules

Data used to create the Military Deployment Index and across our dashboard come from the International Institute for Strategic Studies. Data on population come from the World Bank. The app was developed using open-source frameworks from [plotly](https://plotly.com/): [plotly.py](https://github.com/plotly/plotly.py) and [Dash](https://github.com/plotly/dash).

  

Several adjustments were made to the data upon obtaining them to account for the requirements of our research design or treat inaccuracies contained in the original data source. First, names of oceans and seas were standardized across our database. This has required a manual rewriting of a number of observations due to source-based discrepancies which were of particular importance in cases where locations for a single operation had a distinct coding for each year.


*Example: The location of the Combined Task Force 150, a naval operation under the command of* 
*Combined Maritime Forces, was coded as Arabian Sea in some years and as Gulf of Aden in others.*
  

In this and similar situations, we used operation-specific sources to determine the continuation of a given location and make the necessary changes if confirmed. In a limited number of cases, minor adjustments were made to the longitude and latitude of oceans and seas for design and user-experience purposes. Locations were also re-coded for operations taking place in disputed regions or multiple theaters at once.

  

*Example: The location of the United Nations Truce Supervision Organization (UNTSO) was* *simultaneously set to Egypt, Israel, Jordan, Lebanon, and Syria by the original source. As we* *require a single location per operation for visual purposes, the new coordinates were set to a* *point of equal distance vis-à-vis each original location. In this case, the longitude and* *latitude correspond to the territory of Israel.*

  

Next, a major addition to the original source was required to create an accurate distribution of individual operations in command structures. By a command structure, we mean the designated organization or country leading a given operation. Roughly a third of all observations were missing values for command, namely operations conducted outside of the auspices of international organizations like the UN or NATO. Operation-specific sources were thus used to supplement these cases.

  

*Example: Operation Inherent Resolve, the multilateral military coalition against the Islamic* *State in Iraq and Syria, was missing a value under the category of command. As the United States* 
*is known to be the operation leader in this case, the missing value was changed to ‘USA’ in our* *database.*

  

Third, the original source stopped distinguishing between military observers and regular troops in the deployment figures published past 2020. In order to keep our data standardized, the values for both categories were combined for all years prior to 2020.

  

Finally, we created an additional category to capture the difference between operational deployments abroad and military presence including domestic deployments to overseas territories and permanent bases. Observations were divided based on information provided by the IISS and verified against different government sources. Figures falling under the category of military presence are available after pressing the brown toggle switch in the top-left corner of the map.