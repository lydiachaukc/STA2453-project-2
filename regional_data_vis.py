import plotly.express as px
import pandas as pd
import json

# Only visualize the features below
FEATURES = ['percent_at_least_one_dose',
            'percent_fully_vaccinated',
            'percent_3doses',
            'active_cases',
            'resolved_cases',
            'deaths',
            'percent_active_cases',
            'percent_deaths',
            'percent_resolved_cases']

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
                                   )
        return fig



if __name__ == "__main__":
    rdv = RegDataVis()
    import pdb;pdb.set_trace()
