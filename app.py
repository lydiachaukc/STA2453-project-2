from dash import Input, Output, Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import date

from data import get_vanilla_df
from regional_data_vis import RegDataVis
from vac_data_vis import VacDataVis

# Define application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

vdv = VacDataVis()
rdv = RegDataVis()
date_picker = dcc.DatePickerSingle(
    id='date_picker',
    min_date_allowed=max(rdv.date_range[0], vdv.date_range[0]),
    max_date_allowed=min(rdv.date_range[1], vdv.date_range[1]),
    date=min(rdv.date_range[1], vdv.date_range[1])
)

# Create vaccine cards
cards_r1 = dbc.CardGroup(
    [
    dbc.Card(
        [
            html.H5("Select date:"),
            date_picker,
        ],
        body=True,
        color='whitesomke'
    ),
    dbc.Card(
        [
            html.H5("Doses Administered"),
            html.H2(id="total_doses_administered",
                    style={'color': 'black'}),
            html.H4(id="previous_day_total_doses_administered",
                    style={'color': 'darkgray'})
        ],
        body=True,
        color='ghostwhite'
    ),
    dbc.Card(
        [
            html.H5("1 Dose Received"),
            html.H2(id="percent_at_least_one",
                    style={'color': 'black'}),
            html.H4(id="previous_day_at_least_one",
                    style={'color': 'darkgray'})
        ],
        body=True,
        color='whitesomke'
    ),
    dbc.Card(
        [
            html.H5("2 Doses Received"),
            html.H2(id="percent_fully_vaccinated",
                    style={'color': 'black'}),
            html.H4(id="previous_day_fully_vaccinated",
                    style={'color': 'darkgray'})
        ],
        body=True,
        color='ghostwhite'
    ),
    ])

cards_r2 = dbc.CardGroup(
    [
    dbc.Card(
        [
            html.H5("3 Doses Received"),
            html.H2(id="percent_3doses",
                    style={'color': 'black'}),
            html.H4(id="previous_day_3doses",
                    style={'color': 'darkgray'})
        ],
        body=True,
        color='ghostwhite'
    ),
    dbc.Card(
        [
            html.H5("Active Cases per 100k"),
            html.H2(id="active_cases_per100k",
                    style={'color': 'black'}),
            html.H4(id="active_cases",
                    style={'color': 'darkgray'})
        ],
        body=True,
        color='whitesomke'
    ),
    dbc.Card(
        [
            html.H5("Deaths per 100k"),
            html.H2(id="deaths_per100k",
                    style={'color': 'black'}),
            html.H4(id="deaths",
                    style={'color': 'darkgray'})
        ],
        body=True,
        color='ghostwhite'
    ),
    dbc.Card(
        [
            html.H5("Resolved Cases per 100k"),
            html.H2(id="resolved_cases_per100k",
                    style={'color': 'black'}),
            html.H4(id="resolved_cases",
                    style={'color': 'darkgray'})
        ],
        body=True,
        color='whitesomke'
    ),
    ])

# Create regional vaccination map
vaccine_map = html.Div(
    [
        dcc.Dropdown(
            dict(zip(rdv.vacc_metrics, rdv.vacc_display)),
            "percent_fully_vaccinated",
            id="vaccine_metric_dropdown",
            clearable=False,
        ),
        dcc.Loading(
            id='vacc_map_loading',
            children=[dcc.Graph(id="vaccine_map")],
            type='default'
        ),
    ]
)

case_map = html.Div(
    [
        dcc.Dropdown(
            dict(zip(rdv.case_metrics,rdv.case_display)),
            "active_cases_per100k",
            id="case_metric_dropdown",
            clearable=False,
        ),
        dcc.Loading(
            id='case_map_loading',
            children=[dcc.Graph(id="case_map")],
            type='default'
        ),
    ]
)

tabs = html.Div(
    [
        dbc.Tabs(
            [
            dbc.Tab(label='ICU Rate', tab_id='icu'),
            dbc.Tab(label='Non-ICU Hospitalization Rate', tab_id='non_icu'),
            dbc.Tab(label='Death Rate', tab_id='death_rate'),
            dbc.Tab(label='Vaccination Status', tab_id='vac_percentage'),
            ],
            id="line_graph_tabs",
            active_tab="icu",
        ),
        dcc.Loading(
            id='line_graph_loading',
            children=[dcc.Graph(id="line_graph")],
            type='default'
        ),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row([dbc.Col(html.H2('Ontario Covid-19 Vaccination Dashboard', style={"margin-top": 20}), md=9)]),
        html.Hr(),
        dbc.Row(cards_r1),
        dbc.Row(cards_r2),
        html.Br(),
        # dbc.Row([dbc.Col(html.H4('Select date:'), width=2),
        #          dbc.Col(date_picker)]),
        dbc.Row([dbc.Col(vaccine_map),dbc.Col(case_map)]),
        html.Br(),
        dbc.Row(dbc.Col(html.H4('Time Series Data'))),
        dbc.Row(tabs),
        html.Footer("Data gathered from Ontario goverment open datasets.",
                    style={'color': 'darkgray'})

        # # Side by Slider
        # dbc.Row([dbc.Col([html.H4('New Cases'), new_cases_tabs]),
        #          dbc.Col([html.H4('New Deaths'), new_deaths_tabs])]),
    ],
)


@app.callback(Output("total_doses_administered", "children"), Input("date_picker", "date"))
def update_num(date):
    return vdv.get_data_point(date, "total_doses_administered")

@app.callback(Output("previous_day_total_doses_administered", "children"), Input("date_picker", "date"))
def update_num(date):
    return "+" + str(int(vdv.get_data_point(date, "previous_day_total_doses_administered")))

@app.callback(Output("percent_at_least_one", "children"), Input("date_picker", "date"))
def update_num(date):
    return "{:.2f}".format(vdv.get_data_point(date, "percent_at_least_one")) + "%"

@app.callback(Output("previous_day_at_least_one", "children"), Input("date_picker", "date"))
def update_num(date):
    return "+" + str(int(vdv.get_data_point(date, "previous_day_at_least_one"))) + " doses"

@app.callback(Output("percent_fully_vaccinated", "children"), Input("date_picker", "date"))
def update_num(date):
    return "{:.2f}".format(vdv.get_data_point(date, "percent_fully_vaccinated")) + "%"

@app.callback(Output("previous_day_fully_vaccinated", "children"), Input("date_picker", "date"))
def update_num(date):
    return "+" + str(int(vdv.get_data_point(date, "previous_day_fully_vaccinated"))) + " doses"

@app.callback(Output("percent_3doses", "children"), Input("date_picker", "date"))
def update_num(date):
    return "{:.2f}".format(vdv.get_data_point(date, "percent_3doses")) + "%"

@app.callback(Output("previous_day_3doses", "children"), Input("date_picker", "date"))
def update_num(date):
    return "+" + str(int(vdv.get_data_point(date, "previous_day_3doses"))) + " doses"

@app.callback(Output("active_cases_per100k", "children"), Input("date_picker", "date"))
def update_num(date):
    return "{:.2f}".format(vdv.get_data_point(date, "active_cases_per100k"))

@app.callback(Output("active_cases", "children"), Input("date_picker", "date"))
def update_num(date):
    return str(int(vdv.get_data_point(date, "active_cases"))) + " in total"

@app.callback(Output("deaths_per100k", "children"), Input("date_picker", "date"))
def update_num(date):
    return "{:.2f}".format(vdv.get_data_point(date, "deaths_per100k"))

@app.callback(Output("deaths", "children"), Input("date_picker", "date"))
def update_num(date):
    return str(int(vdv.get_data_point(date, "deaths"))) + " in total"

@app.callback(Output("resolved_cases_per100k", "children"), Input("date_picker", "date"))
def update_num(date):
    return "{:.2f}".format(vdv.get_data_point(date, "resolved_cases_per100k"))

@app.callback(Output("resolved_cases", "children"), Input("date_picker", "date"))
def update_num(date):
    return str(int(vdv.get_data_point(date, "resolved_cases"))) + " in total"

@app.callback(Output("vaccine_map", "figure"), [Input("vaccine_metric_dropdown", "value"), Input("date_picker", "date")])
def update_map(feature, date):
    fig = rdv.get_map_figure(feature, date)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),)
    return fig

@app.callback(Output("case_map", "figure"), [Input("case_metric_dropdown", "value"), Input("date_picker", "date")])
def update_map(feature, date):
    fig = rdv.get_map_figure(feature, date)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),)
    return fig

@app.callback(Output("line_graph", "figure"), Input("line_graph_tabs", "active_tab"))
def switch_tab(tab):
    if tab == 'vac_percentage':
        df = vdv.df.copy()
        df['at_least_one_dose'] = df['percent_at_least_one']
        df['fully_vaccinated'] = df['percent_fully_vaccinated']
        df['3_doses'] = df['percent_3doses']
        fig = px.line(df,
                      x='date',
                      y=['at_least_one_dose','fully_vaccinated','3_doses'],
                      )
        fig.update_layout(xaxis_title="Date",
                          yaxis_title="Percentage",
                          yaxis_range=[0,100],
                          hovermode = 'x',
                          )
    elif tab == 'icu':
        df = pd.read_csv('vaccine_data/line_graph1_data.csv')
        df['fully_vaccinated'] = df['basispt_icu_full_vac']
        df['unvaccinated'] = df['basispt_icu_unvac']
        fig = px.line(df,
                      x='date',
                      y=['fully_vaccinated','unvaccinated'],
                      )
        fig.update_layout(xaxis_title="Date",
                          yaxis_title="Per 100k",
                          hovermode = 'x',
                          )
    elif tab == 'non_icu':
        df = pd.read_csv('vaccine_data/line_graph1_data.csv')
        df['fully_vaccinated'] = df['basispt_hospitalnonicu_full_vac']
        df['unvaccinated'] = df['basispt_hospitalnonicu_unvac']
        fig = px.line(df,
                      x='date',
                      y=['fully_vaccinated','unvaccinated'],
                      )
        fig.update_layout(xaxis_title="Date",
                          yaxis_title="Per 100k",
                          hovermode = 'x',
                          )
    elif tab == 'death_rate':
        df = pd.read_csv('vaccine_data/line_graph2_data.csv')
        df['fully_vaccinated'] = df['deaths_full_vac_rate_7ma']
        df['unvaccinated'] = df['deaths_not_full_vac_rate_7ma']
        fig = px.line(df,
                      x='date',
                      y=['fully_vaccinated','unvaccinated'],
                      )
        fig.update_layout(xaxis_title="Date",
                          yaxis_title="Per 100k",
                          hovermode = 'x',
                          )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
