from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import datetime

##############################################################################
# Gov of Ontario open covid & vaccine data
##############################################################################

class DataLoader():
    def __init__(self, file_type='.csv',
                 urls =['https://data.ontario.ca/en/dataset/covid-19-vaccine-data-in-ontario',
                       'https://data.ontario.ca/en/dataset/deaths-involving-covid-19-by-vaccination-status',
                       'https://data.ontario.ca/en/dataset/status-of-covid-19-cases-in-ontario-by-public-health-unit-phu'],
                 outpath='vaccine_data/',
                 reload_data = False):
        self.urls = urls
        self.file_type = file_type
        self.outpath = outpath
        self.datalinks = self.get_datalinks(urls)
        self.update_data()


    def reload_data(self):
        self.get_datalinks(self.urls)
        self.update_data()


    def get_soup(self, url):
        return bs(requests.get(url).text, 'html.parser')


    def get_datalinks(self, url_list):
        data_links = {}
        for url in url_list:
            for link in self.get_soup(url).find_all('a'):
                csv_link = link.get('href')
                if self.file_type in csv_link:
                    data_links[csv_link.split('/')[-1].replace('.csv','')] = csv_link

        return data_links


    def update_data(self):
        #-- Downloading Data --------------------------------------------------
        vac_status_hosp_icu_data = pd.read_csv(self.datalinks['vac_status_hosp_icu']) #icu, hospitalization cases
        deaths_by_vac_status = pd.read_csv(self.datalinks['deaths_by_vac_status']) #death cases
        cases_by_vac_status_data = pd.read_csv(self.datalinks['cases_by_vac_status']) #new case
        vaccine_count_data = pd.read_csv(self.datalinks['vaccines_by_age']) #vaccine count

        vaccines_by_age_phu_data = pd.read_csv(self.datalinks['vaccines_by_age_phu']) #vaccine rate by phu
        cases_by_status_and_phu_data = pd.read_csv(self.datalinks['cases_by_status_and_phu']) #vaccine rate by phu

        #-- Data Cleaning -----------------------------------------------------
        deaths_by_vac_status = deaths_by_vac_status[deaths_by_vac_status['age_group']=='ALL'].drop('age_group', axis=1)
        cases_by_vac_status_data = cases_by_vac_status_data.drop(
            ['cases_unvac_rate_7ma', 'cases_partial_vac_rate_7ma', 'cases_full_vac_rate_7ma'], axis = 1).rename(columns={'Date': 'date'}).dropna(axis=0)
        vaccine_count_data = vaccine_count_data.drop("Second_dose_cumulative", axis=1).dropna().rename(columns={'Date': 'date'})
        vaccine_count_data = vaccine_count_data[vaccine_count_data['Agegroup'].isin(['Ontario_5plus'])].drop("Agegroup", axis=1)
        vaccine_count_data['unvaccinated']=vaccine_count_data["Total population"]-vaccine_count_data["At least one dose_cumulative"]

        vac_status_hosp_icu_data['date'] = pd.to_datetime(vac_status_hosp_icu_data['date'])
        deaths_by_vac_status['date'] = pd.to_datetime(deaths_by_vac_status['date'])
        cases_by_vac_status_data['date'] = pd.to_datetime(cases_by_vac_status_data['date'])
        vaccine_count_data['date'] = pd.to_datetime(vaccine_count_data['date'])
        vaccines_by_age_phu_data['Date'] = pd.to_datetime(vaccines_by_age_phu_data['Date'])
        cases_by_status_and_phu_data['FILE_DATE'] = pd.to_datetime(cases_by_status_and_phu_data['FILE_DATE'])

        cases_by_status_and_phu_data['PHU_NAME']=cases_by_status_and_phu_data['PHU_NAME'].str.replace('OXFORD ELGIN-ST.THOMAS','SOUTHWESTERN')
        cases_by_status_and_phu_data = cases_by_status_and_phu_data.rename(columns={'FILE_DATE': 'date'})

        vaccines_by_age_phu_data = vaccines_by_age_phu_data.drop(['PHU ID','Second_dose_cumulative'], axis=1).rename(columns={'PHU name': 'PHU_NAME', 'Date': 'date'}).dropna(axis=0)
        vaccines_by_age_phu_data = vaccines_by_age_phu_data[vaccines_by_age_phu_data['Agegroup'].isin(['Ontario_5plus'])].drop('Agegroup', axis=1)
        vaccines_by_age_phu_data = vaccines_by_age_phu_data[vaccines_by_age_phu_data['PHU_NAME']!='UNKNOWN']

        #-- Data Aggregation --------------------------------------------------
        vaccine_case_data = vac_status_hosp_icu_data.join(
                cases_by_vac_status_data.set_index('date'), how='inner', on='date').join(
                vaccine_count_data.set_index('date'), how='inner', on='date')

        regional_data = vaccines_by_age_phu_data.join(
            cases_by_status_and_phu_data.set_index(['date', 'PHU_NAME']),
            on=['date', 'PHU_NAME'], how='inner')

        #-- Data Cleaning 2----------------------------------------------------
        regional_data['PHU_NUM'] = regional_data['PHU_NUM'].astype(int)
        regional_data.columns = regional_data.columns.str.lower()
        regional_data.columns = [col.replace(' ', '_') for col in regional_data.columns]
        regional_data['percent_at_least_one_dose'] *= 100
        regional_data['percent_fully_vaccinated'] *= 100
        regional_data['percent_3doses'] *= 100

        #-- Data Aggregation 2-------------------------------------------------
        regional_data['percent_active_cases'] = regional_data['active_cases'] / regional_data['total_population'] * 100
        regional_data['percent_deaths'] = regional_data['deaths'] / regional_data['total_population'] * 100
        regional_data['percent_resolved_cases'] = regional_data['resolved_cases'] / regional_data['total_population'] * 100
        
        line_graph1 = pd.DataFrame()
        line_graph1['basispt_icu_unvac'] = vaccine_case_data['icu_unvac']/vaccine_case_data['unvaccinated'] * 100000
        line_graph1['basispt_icu_full_vac'] = vaccine_case_data['icu_full_vac']/vaccine_case_data['fully_vaccinated_cumulative'] * 100000
        line_graph1['basispt_hospitalnonicu_unvac'] = vaccine_case_data['hospitalnonicu_unvac']/vaccine_case_data['unvaccinated'] * 100000
        line_graph1['basispt_hospitalnonicu_full_vac'] = vaccine_case_data['hospitalnonicu_full_vac']/vaccine_case_data['fully_vaccinated_cumulative'] * 100000
        line_graph1['basispt_new_cases_unvac'] = vaccine_case_data['covid19_cases_unvac']/vaccine_case_data['unvaccinated'] * 100000
        line_graph1['basispt_new_cases_full_vac'] = vaccine_case_data['covid19_cases_full_vac']/vaccine_case_data['fully_vaccinated_cumulative'] * 100000
        line_graph1['date'] = vaccine_case_data['date']
        
        chart_num = pd.DataFrame()
        chart_num['current_total_hostpitalized_case'] = vaccine_case_data['icu_unvac'] + vaccine_case_data['icu_partial_vac'] + vaccine_case_data['icu_full_vac']
        chart_num['current_total_hostpitalized_case'] += vaccine_case_data['hospitalnonicu_unvac'] + vaccine_case_data['hospitalnonicu_partial_vac'] + vaccine_case_data['hospitalnonicu_full_vac']
        chart_num['change_current_total_hostpitalized_case'] = chart_num['current_total_hostpitalized_case'] - chart_num['current_total_hostpitalized_case'].shift(1)
        
        chart_num['date'] = vaccine_case_data['date']
        chart_num = chart_num.set_index('date')
        
        regional_data_agg = regional_data.groupby(['date']).sum()
        chart_num['fully_vaccinated_cumulative'] = regional_data_agg['fully_vaccinated_cumulative']
        chart_num['change_in_fully_vaccinated_cumulative'] = regional_data_agg['fully_vaccinated_cumulative'] - chart_num['fully_vaccinated_cumulative'].shift(1)
        
        chart_num['active_cases'] = regional_data_agg['active_cases']
        chart_num['change_in_active_cases'] = chart_num['active_cases'] - chart_num['active_cases'].shift(1)
        
        chart_num['deaths_cummulative'] = regional_data_agg['deaths']
        chart_num['change_in_deaths_cummulative'] = chart_num['deaths_cummulative'] - chart_num['deaths_cummulative'].shift(1)
        
        chart_num = chart_num.dropna()
        
        #-- Exporting Data ----------------------------------------------------
        line_graph1.to_csv(self.outpath + "line_graph1_data" + self.file_type, index=False)
        regional_data.to_csv(self.outpath + "regional_data" + self.file_type, index=False)
        deaths_by_vac_status.to_csv(self.outpath + "line_graph2_data" + self.file_type, index=False)
        chart_num.to_csv(self.outpath + "chart_num" + self.file_type)


if __name__ == '__main__':
    test = DataLoader()
