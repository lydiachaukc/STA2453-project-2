import plotly.express as px
import pandas as pd
import json

# Only visualize the features below
FEATURES = ['percent_at_least_one_dose',
            'percent_fully_vaccinated',
            'percent_3doses',
            'active_cases_per100k',
            'deaths_per100k',
            'resolved_cases_per100k']
VACC_METRICS = ['percent_at_least_one_dose',
                'percent_fully_vaccinated',
                'percent_3doses',]
CASE_METRICS = ['active_cases_per100k',
                'deaths_per100k',
                'resolved_cases_per100k']
VACC_DISPLAY= ['Percentage of At Least One Dose',
                'Percentage of Fully Vaccinated',
                'Percentage of Three Doses']
CASE_DISPLAY = ['Active Cases',
                'Deaths',
                'Resolved Cases']

# Path to data files
REGIONAL_DATA_PATH = "vaccine_data/regional_data.csv"
GEOJSON_PATH = "vaccine_data/Ministry_of_Health_Public_Health_Unit_Boundary.geojson"

class RegDataVis():
    def __init__(self):
        self.df = pd.read_csv(REGIONAL_DATA_PATH)
        with open(GEOJSON_PATH) as f:
            geomap = json.load(f)
        self.geomap = geomap
        self.regions = list(set(self.df["phu_name"].tolist()))
        self.features = FEATURES
        self.vacc_metrics = VACC_METRICS
        self.case_metrics = CASE_METRICS
        self.vacc_display = VACC_DISPLAY
        self.case_display = CASE_DISPLAY
        self.date_range = (min(self.df['date']), max(self.df['date']))

    def reload_data(self):
        self.df = pd.read_csv(REGIONAL_DATA_PATH)
        with open(GEOJSON_PATH) as f:
            geomap = json.load(f)
        self.geomap = geomap
        self.regions = list(set(self.df["phu_name"].tolist()))
        self.date_range = (min(self.df['date']), max(self.df['date']))

    def get_df(self, date=None, region=None):
        result = self.df.copy()
        if date:
            assert date >= self.date_range[0]
            assert date <= self.date_range[1]
            result = result[result['date'] == date]
        if region:
            assert region in self.regions
            result = result[result['phu_name'] == region]

        return result

    def get_map_figure(self, feature, date=None):
        if not date:
            date = self.date_range[1]
        partial_df = self.get_df(date=date)

        # If feature is positive, use cooler coler
        color_scale = 'mint' if 'dose' in feature or 'vac' in feature else 'oranges'

        # Create map figure
        labels = dict(zip(self.features, ["Percent "] * 3 + ["Case per 100k "] * 3))
        fig = px.choropleth_mapbox(partial_df,
                                   geojson=self.geomap,
                                   featureidkey="properties.PHU_ID",
                                   locations='phu_num',
                                   color=feature,
                                   hover_name="phu_name",
                                   hover_data=self.features,
                                   color_continuous_scale=color_scale,
                                   mapbox_style="carto-positron",
                                   zoom=3,
                                   center = {"lat": 49.26713948584354, "lon": -86.43758876897996},
                                   labels=labels
                                   )
        
        return fig



if __name__ == "__main__":
    rdv = RegDataVis()
    import pdb;pdb.set_trace()
