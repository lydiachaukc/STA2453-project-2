from dash import Input, Output, Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import date

from data import get_vanilla_df
from regional_data_vis import RegDataVis

# Define application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Dict of possible time deltas
delta_to_day = {'2W':14, '1M':30, '3M': 90, '6M':180, '9M':270, '1Y':365, 'Max':None}

# Get data
df_can = get_vanilla_df()
df = df_can

# Get today's data point
def get_today(key):
    date_today = max(df['date'])
    return df[df['date'] == date_today][key].tolist()[0]

total_cases = int(get_today('total_cases'))
new_cases = int(get_today('new_cases'))
total_deaths = int(get_today('total_deaths'))
new_deaths = int(get_today('new_deaths'))

def get_new_cases_fig(df):
    fig = px.area(x= df['date'],
                  y = df['new_cases_smoothed'],
                  color=px.Constant("Smoothed"),
                  )
    fig.add_bar(x= df['date'], y = df['new_cases'], name = 'Actual')
    fig.update_layout(xaxis_title="Date",
                      yaxis_title="New Cases",
                      hovermode = 'x',
                      )
    return fig

def get_new_deaths_fig(df):
    fig = px.area(x= df['date'],
                  y = df['new_deaths_smoothed'],
                  color=px.Constant("Smoothed"),
                  )
    fig.add_bar(x= df['date'], y = df['new_deaths'], name = 'Actual')
    fig.update_layout(xaxis_title="Date",
                      yaxis_title="New Deaths",
                      hovermode = 'x',
                      )
    return fig

def get_tab_content(delta, plotting_func):
    assert delta in delta_to_day

    df = df_can
    if delta != "Max":
        date_max = max(df['date'])
        day_delta = pd.Timedelta(days=delta_to_day[delta])
        date_min = date_max - day_delta
        df = df_can[df_can['date'] >= date_min]

    return plotting_func(df)

new_cases_tabs = html.Div(
    [
        dbc.Tabs(
            [dbc.Tab(label=delta, tab_id=delta) for delta in delta_to_day],
            id="new_cases_tabs",
            active_tab="Max",
        ),
        dcc.Loading(
            id='new_cases_graph_loading',
            children=[dcc.Graph(id="new_cases_graph")],
            type='default'
        ),
    ]
)
new_deaths_tabs = html.Div(
    [
        dbc.Tabs(
            [dbc.Tab(label=delta, tab_id=delta) for delta in delta_to_day],
            id="new_deaths_tabs",
            active_tab="Max",
        ),
        dcc.Loading(
            id='new_deaths_graph_loading',
            children=[dcc.Graph(id="new_deaths_graph")],
            type='default'
        ),
    ]
)

# Create regional vaccination map
rdv = RegDataVis()
date_picker = dcc.DatePickerSingle(
    id='date_picker',
    min_date_allowed=rdv.date_range[0],
    max_date_allowed=rdv.date_range[1],
    date=rdv.date_range[1]
)

vaccine_map = html.Div(
    [
        dcc.Dropdown(
            rdv.vacc_metrics,
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
            rdv.case_metrics,
            "percent_active_cases",
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

cards = dbc.CardGroup(
    [dbc.Card(
        [
            html.H5("Cases"),
            html.H2(str(total_cases)),
            html.H2("+" + str(new_cases))
        ],
        body=True,
        color='ice'
    ),
    dbc.Card(
        [
            html.H5("Deaths"),
            html.H2(str(total_deaths)),
            html.H2("+" + str(new_deaths))
        ],
        body=True,
        color='ice'
    ),
    dbc.Card(
        [
            html.H5("Select date:"),
            date_picker,
        ],
        body=True,
        color='ice'
    ),])

app.layout = dbc.Container(
    [
        dbc.Row([dbc.Col(html.H2('Ontario Covid-19 Vaccination Dashboard', style={"margin-top": 20}), md=9)]),
        html.Hr(),
        dbc.Row(cards),
        html.Br(),
        # dbc.Row([dbc.Col(html.H4('Select date:'), width=2),
        #          dbc.Col(date_picker)]),
        dbc.Row([dbc.Col(vaccine_map),dbc.Col(case_map)]),
        html.Br(),
        dbc.Row(dbc.Col(html.H4('New Cases'))),
        dbc.Row(new_cases_tabs),
        dbc.Row(dbc.Col(html.H4('New Deaths'))),
        dbc.Row(new_deaths_tabs),

        # # Side by Slider
        # dbc.Row([dbc.Col([html.H4('New Cases'), new_cases_tabs]),
        #          dbc.Col([html.H4('New Deaths'), new_deaths_tabs])]),
    ],
)

@app.callback(Output("new_cases_graph", "figure"), Input("new_cases_tabs", "active_tab"))
def switch_tab1(delta):
    return get_tab_content(delta, get_new_cases_fig)

@app.callback(Output("new_deaths_graph", "figure"), Input("new_deaths_tabs", "active_tab"))
def switch_tab2(delta):
    return get_tab_content(delta, get_new_deaths_fig)

@app.callback(Output("vaccine_map", "figure"), [Input("vaccine_metric_dropdown", "value"), Input("date_picker", "date")])
def update_map(feature, date):
    return rdv.get_map_figure(feature, date)

@app.callback(Output("case_map", "figure"), [Input("case_metric_dropdown", "value"), Input("date_picker", "date")])
def update_map(feature, date):
    return rdv.get_map_figure(feature, date)


if __name__ == '__main__':
    app.run_server(debug=True)
