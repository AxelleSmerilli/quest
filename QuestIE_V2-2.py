#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# Packages

# In[1]:


import pandas as pd
import plotly.express as px
 
from datetime import datetime, timedelta





# In[3]:


from dash import Dash
from dash import dcc, html
from dash.dependencies import Input, Output






# In[6]:


import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template





# Import data

# In[7]:


# load the data
full = pd.read_csv('full.csv')
df = full.rename(columns={'TradeValue in 1000 USD': 'Value'}).groupby(['Use','ProductCode', 'PartnerISO3','PartnerName','Year']).Value.sum().reset_index()
df = df.fillna(0)

product_names = pd.read_csv('codename.csv', sep =";")

df = df.merge(product_names,how = 'inner', on = "ProductCode")

df.Value = df.Value*1000
# create a list of countries
countries = df.PartnerName.unique()

# create a list of products
products = product_names.ProductName.unique()

# create a list of years
years = df.Year.unique()

# create a list of uses
uses = df.Use.unique()








# create a dash app
app = Dash(external_stylesheets = [dbc.themes.LUX])
server = app.server
# create a dash app layout
# create a dash app layout
app.layout = html.Div([
    html.H1('Supply in nuclear energy for South Korea'),
    
    html.Br(),
    
    html.P('Choose for which element you want to display products used in:'),
    
    dbc.Row(
        children = [
            dcc.Dropdown(
                id='use', 
                options=[{'label': i, 'value': i} for i in uses], 
                value=uses[0], 
                multi=False
            )
        ]
    ),
    
    html.Br(),
    
    html.P('Specify which products you are interested in:'),
    
    dbc.Row(
        children = [
            dcc.Dropdown(
                id='product', 
                value = products,
                multi = True
            )
        ]
    ),
    
    html.Br(),
    
    dbc.Row(
        children = [
            dbc.Col(html.P('Pick a year of data for the map:')),
            dbc.Col(
                dcc.Dropdown(
                    id='year', 
                    options=[{'label': i, 'value': i} for i in years], 
                    value=max(years)
                ),
                className = 'two columns'
            )
        ]
    ),
    
   html.Br(), 
    
    dbc.Row(
        children = [
            dbc.Col(dcc.Graph(id='map-graph', className = 'six columns'))
        ]
    ),
    
    html.Br(),
    
    html.P('Unselect the countries to not be taken into account:'),
    
    dbc.Row(
        children = [
            dcc.Dropdown(
                id='country', 
                options=[{'label': i, 'value': i} for i in countries], 
                value=countries, 
                multi=True
            )
        ]
    ),
    
    html.Br(),
    
    
    dbc.Row(
        children = [
            html.Div([
                dcc.Graph(id='timeseries-graph-by-countries'),
                dcc.Graph(id='timeseries-graph-by-products'), 
        ])
        ]
    )

],
style = {'margin' : '30px'})





# callback for the product button dependinc on combustion / gaines / barres de contrôle
@app.callback(
    Output('product', 'options'),
    Output('product', 'value'),
    Input('use', 'value')
)

def produits(use):
    products = df[df['Use']==use].ProductName.unique()
    options = [{'label': i, 'value' : i} for i in products]
    
    return options, products

# create a callback for the timeseries graph
@app.callback(
    Output('timeseries-graph-by-countries', 'figure'),
    [
    Input('country', 'value'),
    Input('product', 'value')
    ])
def update_countries_graph(countries, products):
    # filter the data
    dff = df[(df.PartnerName.isin(countries)) & (df.ProductName.isin(products))]
    dff = dff.groupby(['Year','PartnerName']).Value.sum().reset_index()
    # create a timeseries graph
    fig = px.line(dff, 
        x='Year', 
        y='Value', 
        color='PartnerName', 
        title='Timeseries by Countries'
    )
    
    fig.update_layout(
        title = "Products' traded value (in USD) combined since 2015 by country",
        xaxis_title = "Year",
        yaxis_title = 'Traded value in USD', 
        legend_title_text = 'Countries'
    )
    
    return fig

# create a callback for the timeseries graph
@app.callback(
    Output('timeseries-graph-by-products', 'figure'),
    [
    Input('country', 'value'),
    Input('product', 'value')
    ])
def update_products_graph(countries, products):
    # filter the data
    dff = df[(df.PartnerName.isin(countries)) & (df.ProductName.isin(products))]
    dff = dff.groupby(['Year','ProductName']).Value.sum().reset_index()
    # create a timeseries graph
    fig = px.line(dff, 
        x='Year', 
        y='Value', 
        color='ProductName', 
        #title='Timeseries by Products'
    )
    
    fig.update_layout(
        title = "Products' traded value (in USD) since 2015, all countries combined",
        xaxis_title = "Year",
        yaxis_title = 'Traded value in USD', 
        legend_title_text = 'Products'
    )
    
    return fig

# create a callback for the map graph
@app.callback(
    Output('map-graph', 'figure'),
    [
    Input('product', 'value'),
    Input('year', 'value'),

    ])
def update_map_graph(products, year):
    # filter the data
    dff = df[df['Year'] == year]
    dff = dff[(dff.ProductName.isin(products))]
    dff = dff.groupby(['Year','PartnerISO3','PartnerName']).Value.sum().reset_index()
    # create a map graph
    fig = px.scatter_geo(dff, 
        locations='PartnerISO3', 
        hover_name='PartnerName', 
        locationmode = 'ISO-3',
        size='Value',

    )
    fig.update_layout(
        title="Products' value supplied per country in " + str(year),
        geo_showcountries = True)

    return fig

# run the app
#if __name__ == '__main__':
app.run_server(debug=True)





