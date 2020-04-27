#!/usr/bin/env python
# coding: utf-8

# # Global Pandemic: Understanding COVID-19 Trends by Visualization
# -- Jiani Shi


get_ipython().run_line_magic('matplotlib', 'inline')
import pandas as pd
import bqplot
import numpy as np
import matplotlib.pyplot as mplt
from bqplot import pyplot as plt

#read file
f= pd.read_csv("C:/Users/sjnnt/is590dv/COVID-19 Cases_re.csv",dtype = {'Country_Region':str})

co = f['Country_Region'].unique()
ty =  f['Case_Type'].unique()

#aggregate
f_agg = f['Cases'].groupby([f['Country_Region'],f['Date'],f['Case_Type']]).sum().reset_index(name = 'Total_Cases')
mask_1 = (f_agg['Country_Region'].values == co[i]) &(f_agg['Case_Type'].values == ty[j])

time = f_agg['Date'].unique()

q = 50
mask_2 = (f_agg['Case_Type'].values == ty[j]) & (f_agg['Date'].values == time[q])

# read the code file
ios= pd.read_csv("C:/Users/sjnnt/is590dv/countries_codes_and_coordinates.csv",dtype = {'Alpha-3 code':str})

import re
# revise the format of columns
for i in range(0,len(ios)):
    ios['Alpha-3-code'][i] = re.sub('"','',ios['Alpha-3-code'][i]) 
    ios['Alpha-3-code'][i] = re.sub(' ','',ios['Alpha-3-code'][i]) 

f_new = pd.merge(f_agg,ios,on= 'Country_Region',how = 'left')

f_agn = f_new['Total_Cases'].groupby([f_new['Country_Region'],f_new['Date'],f_new['Case_Type'],f_new['Alpha-3-code']]).sum().reset_index(name = 'Total_Cases')

# divided data into two groups
mask_c = f_agn['Case_Type'].values == 'Confirmed'
mask_d = f_agn['Case_Type'].values == 'Deaths'

df = f_agn[mask_c]

#the quick look of choropleth mapbox
import plotly.express as px
fig = px.choropleth(df, locations='Alpha-3-code', 
                    color='Total_Cases',
                    hover_name = "Country_Region",
                    animation_frame = 'Date',
                    projection = "natural earth",
                   title = 'Confirmed Cases of COVID19')

fig.show()

#turn to dash
import dash
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

available_countries = f_new['Country_Region'].unique()

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown( #setting dropdown menu
            id = 'case_type',
            options = [{'label':'Confirmed','value':'Confirmed'},
                       {'label':'Deaths','value':'Deaths'}],
            value = 'Confirmed'
            )
        ],
        style={'width': '48%', 'display': 'inline-block'})
        
    ]),
    html.Div([ # define the id of two figures
        dcc.Graph(id = 'map',
            hoverData={'points': [{'hovertext': 'US'}]})
    ], style={'display': 'inline-block', 'width': '60%'}),
    html.Div([
        dcc.Graph(id = 'line_plot')
    ], style={'width': '40%', 'display': 'inline-block', 'padding': '0 20'})

])

@app.callback(
    Output('line_plot','figure'),
    [Input('case_type','value'),
     Input('map','hoverData')] # hoverdata : mouse over values of the graph
    
)


def update_graph(case_type,hoverData):
    country_name= hoverData['points'][0]['hovertext'] # read the hover data
    dff = f_new[(f_new['Country_Region'] == country_name) & (f_new['Case_Type'] == case_type)]
    return {'data': [dict(
            x =  dff['Date'],
            y = dff['Total_Cases'],
            text = dff['Total_Cases'],
            mode = 'lines+markers'
        )],
        'layout':{
            'xaxis' :{
                'title':'date'
            },
            'yaxis' :{
                'title': country_name,
                'type':'linear'
            },
            'height':450,
            'margin':{'l': 40, 'b': 60, 'r': 0, 't': 0}
            
        }
    }


@app.callback(
    Output('map','figure'),
    [Input('case_type','value')]
)


def create_map(case_type):
    dfff = f_new[f_new['Case_Type']==case_type]
    figure = px.choropleth(dfff, locations='Alpha-3-code', 
                            color='Total_Cases',
                            hover_name = "Country_Region", # hover data
                            animation_frame = 'Date',
                            projection = "natural earth",
                           title = 'Confirmed Cases of COVID19')
    figure.update_layout(hovermode = 'closest')
    return figure

app.run_server()



