from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import datetime
FILETYPE = '.csv'

def get_soup(url):
    return bs(requests.get(url).text, 'html.parser')

##############################################################################
# Gov of Ontario vaccine data
# Detailed description of the data is in https://data.ontario.ca/dataset/752ce2b7-c15a-4965-a3dc-397bf405e7cc/resource/29d182db-69c5-4cfb-894e-35227013689d/download/vaccine_open_data_dictionary_en_fr.xlsx
##############################################################################
ontraio_gov_url = 'https://data.ontario.ca/en/dataset/covid-19-vaccine-data-in-ontario'

data_links = {}
for link in get_soup(ontraio_gov_url).find_all('a'):
    csv_link = link.get('href')
    if FILETYPE in csv_link:
        data_links[csv_link.split('/')[-1].replace('.csv','')] = csv_link
        

cases_by_age_vac_status_data = pd.read_csv(data_links['cases_by_age_vac_status']).drop(
    ['cases_unvac_rate_7ma', 'cases_partial_vac_rate_7ma', 'cases_full_vac_rate_7ma'], axis = 1)

vac_status_hosp_icu_data = pd.read_csv(data_links['vac_status_hosp_icu'])
vaccine_doses_data = pd.read_csv(data_links['vaccine_doses'])

vaccines_by_age_data = pd.read_csv(data_links['vaccines_by_age'])
# vaccines_by_age_phu_data = pd.read_csv(data_links['vaccines_by_age_phu'])


##############################################################################
# JHU CSSE COVID-19 Dataset
# Detailed description of the data is in https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data
##############################################################################
jhu_url = 'https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports'
github_url = 'https://github.com'

data_links = {}
for link in get_soup(jhu_url).find_all('a'):
    csv_link = link.get('href')
    if FILETYPE in csv_link:
        data_links[csv_link.split('/')[-1].replace('.csv','')] = csv_link

ytd_date = str(datetime.date.today() - datetime.timedelta(days=1))
jhu_data = pd.read_csv(github_url + data_links[ytd_date[5:]+"-"+ytd_date[:4]]+'?raw=true')