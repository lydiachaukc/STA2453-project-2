import pandas as pd

def get_vanilla_df():
    # Download data
    df_all = pd.read_csv('https://covid.ourworldindata.org/data/owid-covid-data.csv')
    df_can = df_all[df_all['iso_code'] == 'CAN']

    # Data preprocessing
    df_can['date'] = pd.to_datetime(df_can['date'])
    return df_can
