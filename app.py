import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import datetime as dt
import json
import time

##############
import os
################

from dataprocess import daterange
from dataprocess import DataAggregate, ModelAggregate, EstimateModel
from converters import ZipcodeConvert
import createmap
from geomethods import InterpolationMethods


dbpath = './database/DailyWeather.db'
dbtable = 'DailyWeatherData'
metatable = 'StationInfo'

zipcodepath = './zipcode/us-zip-code-latitude-and-longitude.csv'
jsonpath = os.path.join('static', 'weather.geojson')




firstmap = createmap.FoliumMaps('firstmap').generate_basemap()
firstmap.savemap()
firstmap_path = firstmap.getsavepath()


mindate, maxdate = daterange(dbpath, "DailyWeatherData")
today = dt.datetime.today()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server





navbar = dbc.NavbarSimple(
    children = [
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.NavItem(dbc.NavLink("Source", href="https://www.apsnet.org/publications/phytopathology/backissues/Documents/1996Articles/Phyto86n05_480.pdf")),
        dbc.DropdownMenu(
            children = [
                dbc.DropdownMenuItem("Other models", header = True)
            ],
            nav=True,
            in_navbar=True,
            label = "models",
        )
    ],
    brand = 'Johnson Potato Late Blight Forecast Model',
    color = "dark",
    dark = True,
    fluid=True
    
)

_body = html.Div([

    dbc.Row([
        dbc.Col([
            html.Div([
                html.Label("Enter Your Zipcode")
            ], className = "labels"),

            html.Div([
                dcc.Input(placeholder = "zipcode", type='text', id='zipcode'),
            ], className = "inputs"),

            html.Div([
                html.P(
                    id = 'zipcodeinfo'
                )
            ], className='popupinfo'),

            html.Div([
                html.Label("Was last year an outbreak year?")
            ], className = "labels"),

            html.Div([
                dcc.RadioItems(
                    options = [
                        {'label':'No', 'value':0}, 
                        {'label': 'Yes', 'value':1}
                    ],
                    value = 0,
                    inputStyle = {"marginRight":"0.2rem"},
                    labelStyle = {"marginRight":"0.8rem"},
                    id = 'outbreakyear'
                )
            ], className = "inputs"),
            
            html.Div([
                html.Label("Have you observed outbreak this year?")
            ], className = "labels"),

            html.Div([
                dcc.RadioItems(
                options = [
                    {'label':'No', 'value':0}, 
                    {'label': 'Yes', 'value':1}
                ],
                value = 0,
                inputStyle = {"marginRight":"0.2rem"},
                labelStyle = {"marginRight":"0.8rem"},
                id = 'outbreakyet'
            )
            ], className = "inputs"),

            html.Div([
                html.Label("Pick Date for Prediction:")
            ], className='labels'),

            html.Div([
                dcc.DatePickerSingle(
                    id='pickdate',
                    min_date_allowed = mindate,
                    max_date_allowed = today,
                    initial_visible_month = today
                )
            ], className="inputs"),

            html.Div([
                html.P(
                    id = 'updateinfo'
                )
            ], className="popupinfo"),

            html.Div([
                html.Label("Model Available")
            ], className="labels"),

            html.Div([
                dcc.Dropdown(
                    options = [
                        {'label':'Logistic Model 1', 'value':'log1', 'disabled':True},
                        {'label':'Logistic Model 2', 'value':'log2', 'disabled':True},
                    ],
                    id='models',
                    placeholder = "Available Models",
                    clearable = False
                )
            ], className="inputs"),

            html.Div([
                html.Label("Pick Interpolation (Squared IDW):")
            ], className='labels'),

            html.Div([
                dcc.Dropdown(
                    id='interpolate',
                    options = [
                        {'label':'Simple IDW', 'value':'IDW'},
                        {'label':'Ordinary Kriging', 'value':'Krig'},
                        {'label':'Radical Function', 'value':'Radical'},
                        {'label':'Nearest Neighbor', 'value':'NND'},
                    ],
                    placeholder = "Select an interpolation method",
                    clearable = False,
                    value = "IDW"
                )
            ], className="inputs"),



            html.Button(
                id = 'submit',
                n_clicks = 0,
                children='Submit',
                className = "btn btn-secondary submit-button",
            )

    ], width=2, md=3, className="col1"),

    dbc.Col([
            html.Iframe(id='graph', srcDoc=open(firstmap_path, 'r').read()),
            html.Div([
                html.Label("Risk Value (threshold 0.5):", id='display-label-risk'),
                html.P(id='dRisk'),
            ]),

            html.Div([
                html.Label("Year:", id='display-label-year'),
                html.P(id='dYear'),
            ])
        ], width="auto", md=7, className = "col2")


    ], className="rowpanel"),

    


        
])


def serve_layout():
    return html.Div([

    html.Div([navbar]),

    _body,

    html.Div(
        html.Footer("@2019 Oregon State University Hermiston Agricultural and Research CenterContact: lixiaopi@oregonstate.edu", id='footer')
    )])

app.layout = serve_layout


# @server.route('/static')
# def serve_static(path):
#     return render_template('basemap.html')


# call back for make model available
@app.callback(
    [
        Output(component_id='models', component_property='options'),
        Output(component_id='updateinfo', component_property='children'),
        Output(component_id='updateinfo', component_property='style'),
    ],

    [
        Input(component_id='pickdate', component_property='date'),
        Input(component_id='outbreakyet', component_property='value')
    ]
)
def update_model(inputdate, outbreakyet):


    updateinformation = None
    color = 'rgba(32, 100, 8, 0.9)'
    options = None
    if inputdate is not None:
        
        date_obj = dt.datetime.strptime(inputdate, "%Y-%m-%d")
        year = date_obj.year
        month = date_obj.month

        # for first model to be available: june first,
        # for second model to be available: end of august and no blight observed
        if year == maxdate.year:
            # if pick year is this year
            # check for threshold day
            if month >=6:
                options = [
                    {'label':'Logistic Model 1', 'value':'log1', 'disabled':False},
                    {'label':'Logistic Model 2', 'value':'log2', 'disabled':True},
                    ]
                updateinformation = "Only logistic model #1 is available"

            elif month > 8 and outbreakyet == 0:
                options = [
                    {'label':'Logistic Model 1', 'value':'log1', 'disabled':False},
                    {'label':'Logistic Model 2', 'value':'log2', 'disabled':False},
                ]

                updateinformation = "Logistic model #1 and #2 are available"

            elif month > 8 and outbreakyet == 1:
                options = [
                    {'label':'Logistic Model 1', 'value':'log1', 'disabled':False},
                    {'label':'Logistic Model 2', 'value':'log2', 'disabled':True},
                ]

                updateinformation = "Only logistic model #1 is available"

            else:
                options = [
                    {'label':'Logistic Model 1', 'value':'log1', 'disabled':True},
                    {'label':'Logistic Model 2', 'value':'log2', 'disabled':True},
                ]
                updateinformation = "Sorry, neither model is available yet"
                color = 'rgba(169, 52, 20, 0.9)'

        elif year < maxdate.year:
                options = [
                    {'label':'Logistic Model 1', 'value':'log1', 'disabled':False},
                    {'label':'Logistic Model 2', 'value':'log2', 'disabled':False},
                ]

                updateinformation = "Logistic model #1 and #2 are available"
                
 
    return options, f"{updateinformation}", {'color': color}





@app.callback(

    [
        Output(component_id='dRisk', component_property='children'),
        Output(component_id='dRisk', component_property='style'),
        Output(component_id='dYear', component_property='children'),
        Output(component_id="zipcodeinfo", component_property="children"),
        Output(component_id='zipcodeinfo', component_property="style"),
        Output(component_id='graph', component_property="srcDoc")

    ],
    [
        Input(component_id='submit', component_property='n_clicks')
    ],
    [
        State(component_id='zipcode', component_property='value'),
        State(component_id='outbreakyear', component_property='value'),
        State(component_id='outbreakyet', component_property='value'),
        State(component_id='pickdate', component_property="date"),
        State(component_id='models', component_property='value'),
        State(component_id='interpolate', component_property='value')
        
    ]
)
def update_form(n_clicks,zipcode, outbreakyear, outbreakyet, inputdate, models, interpolate):


    zinfo = None
    valid = True
    

    query_lat = None 
    query_lon = None
    srcDoc = open(firstmap_path, 'r').read()
    df = None

    display_risk = "No data has generated."
    display_year = None
    risk_color = None

    if zipcode is not None:
        if not ZipcodeConvert.checkzipcode(zipcode):
            zinfo = "Invalid Zip Code. 5 digits"
            valid = False
        elif zipcode == "":
            zinfo = "Zip code is empty. Please input zipcode"
            valid = False
        else:
            query_lat, query_lon = ZipcodeConvert(zipcodepath).loadcsv().zipcode_to_coords(zipcode)

    if inputdate is not None and valid and models is not None:

        if int(outbreakyear) == 0:
            Yp = False
        elif int(outbreakyear) == 1:
            Yp = True

        # selected data
        properties = ['Sites', 'state', 'description', 'pval']

        constructor = ModelAggregate(models, Yp, dbpath=dbpath, dbtable=dbtable, metatable=metatable, inputdate=inputdate)
        # to static folder
        constructor.calcModel().df_to_geojson(properties)

        df = constructor.getDataframe()
        # tranformit to numpy array shape (n, 3)
        data = df[['latitude', 'longitude', 'pval']]
        nd_data = data.values


        query_point = [query_lat, query_lon]
        # single data point entry
        # interpolate ram, rja, pp from nearest 10 df
        ram_p = ['latitude', 'longitude', 'RAM']
        rja_p = ['latitude', 'longitude', 'RJA']
        pp_p = ['latitude', 'longitude', 'PP']

        RAM_estimate = InterpolationMethods(df, query_point, ram_p).generateCoordValues().picknearestN(10).pickMethods(interpolate)
        RJA_estimate = InterpolationMethods(df, query_point, rja_p).generateCoordValues().picknearestN(10).pickMethods(interpolate)
        PP_estimate = InterpolationMethods(df, query_point, pp_p).generateCoordValues().picknearestN(10).pickMethods(interpolate)

        estimate_p = EstimateModel(RAM_estimate, RJA_estimate, PP_estimate, Yp).estimatePoint(models)
        
        newmap = "newmap"
        basemap = createmap.FoliumMaps(newmap).generate_basemap()
        basemap.add_heatmap(nd_data)
        basemap.add_circleMarker(query_point, estimate_p)
        basemap.savemap()
        newmap_path = basemap.getsavepath()
        srcDoc = open(newmap_path, 'r').read()

        display_risk = f"{estimate_p}"

        YEAR = dt.datetime.strptime(inputdate, '%Y-%m-%d').year
        display_year = f"{YEAR}"

        if estimate_p >= 0.5:
            risk_color = {'color': 'red'}
        else:
            risk_color = {'color':'green'}


    return  display_risk, risk_color, display_year, zinfo, {'color':'red'}, srcDoc


# clear model, zipcode after submit
@app.callback(
    [
        Output(component_id='zipcode', component_property='value'),
        Output(component_id='models', component_property='value'),
        Output(component_id='interpolate', component_property='value')
    ],
    [Input(component_id='submit', component_property='n_clicks')]
)
def clear_input(n_clicks):
    return "", None, None



if __name__ == '__main__':
    app.run_server()