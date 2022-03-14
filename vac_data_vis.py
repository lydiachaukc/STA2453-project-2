import plotly.express as px
import pandas as pd

# Only visualize the features below
FEATURES = ['total_doses_administered',
            'total_individuals_at_least_one',
            'total_individuals_fully_vaccinated',
            'total_individuals_3doses',
            'previous_day_total_doses_administered',
            'previous_day_at_least_one',
            'previous_day_fully_vaccinated',
            'previous_day_3doses',
            'active_cases',
            'deaths',
            'resolved_cases',
            'percent_at_least_one',
            'percent_fully_vaccinated',
            'percent_3doses',
            'active_cases_per100k',
            'deaths_per100k',
            'resolved_cases_per100k',
            ]

# Path to data files
DATA_PATH = "vaccine_data/vac_main.csv"

class VacDataVis():
    def __init__(self):
        self.df = pd.read_csv(DATA_PATH)
        self.features = FEATURES
        self.date_range = (min(self.df['date']), max(self.df['date']))

    def reload_data(self):
        self.df = pd.read_csv(DATA_PATH)
        self.date_range = (min(self.df['date']), max(self.df['date']))

    def get_df(self, date=None, feature=None):
        result = self.df.copy()
        if date:
            assert date >= self.date_range[0]
            assert date <= self.date_range[1]
            result = result[result['date'] == date]
        if feature:
            assert feature in self.features
            result = result[feature]
        return result

    def get_data_point(self, date, feature):
        assert date >= self.date_range[0]
        assert date <= self.date_range[1]
        assert feature in self.features

        return self.df[self.df['date'] == date][feature].tolist()[0]




if __name__ == "__main__":
    vdv = VacDataVis()
    import pdb;pdb.set_trace()
