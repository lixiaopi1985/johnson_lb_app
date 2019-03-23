import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import datetime as dt
import folium
import json


from dataprocess import ZipcodeConvert, Dbfetch
import geomethods
import riskmodels
import mapit


dbpath = './database/Weather.db'
zipcodepath = './zipcode/us-zip-code-latitude-and-longitude.csv'
SaveMapAs = 'tmp_map_object'

# save map object first
mapobject = mapit.Getmap(SaveMapAs).generate_basemap()
mapobject.savemap()


dbconn = Dbfetch(dbpath)
fetchall = dbconn.fetchAll().Todataframe()
years = fetchall['Year'].values.tolist()
today_date = dt.date.today()
today_year = today_date.year



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = html.Div([

    html.Div([

        html.H1("Potato Late Blight Risk Model", style=dict(fontSize=50, padding=20, fontWeight='bold')),

        html.P("Model Source: Johnson, D.A., Alldredge, J.R. and Vakoch, D.L. 1996. Potato Late Blight forecasting models for the semiarid environment of south-central Washington. Phytopathology 86:486-484", style=dict(fontSize=10, padding = 5, marginTop=0))
    ], style=dict(backgroundColor='rgb(164, 175, 193)')),


    dbc.Container(
        dbc.Row([
            dbc.Col([
                html.Div([

                    dbc.FormGroup([
                        dbc.Label("Zip Code"),
                        dbc.Input(id='zipcode-input',type='text'),
                    ]),

                    dbc.FormGroup([
                        dbc.Label("Calendar"),
                        dbc.DatePickerSingle(id='date-picker',
                        min_date_allowed = dt.datetime(min(years), 1, 1),
                        max_date_allowed = dt.datetime(max(years), 12, 31),
                        initial_visible_month = dt.datetime(max(years), 12, 31)
                        )
                    ]),

                    dbc.FormGroup([
                        dbc.Label('Outbreak observed this year for you location?'),
                        dbc.RadioItems(id='outbreak', options=[{'label': 'Yes', 'value':1}, {'label':'No', 'value':0}], value=0)
                    ]),

                    dbc.FormGroup([
                        dbc.Label('Last year an outbreak year for you location?'),
                        dbc.RadioItems(id='outbreak_prev', options=[{'label': 'Yes', 'value':1}, {'label':'No', 'value':0}], value=0)
                    ]),

                    dbc.FormGroup([
                        dbc.Label('Choose Interpolation Method'),
                        dcc.Dropdown(id='interp-select', options = [{'label': 'Nearest Neighbor', 'value': 'NND'},
                            {'label': 'Linear Nearest Neighbor', 'value':'LND'}
                        ], searchable=False, placeholder = "Select a interpolation method, default: nearest neigbor", value='NND'),
                        
                    ]),

                    dbc.FormGroup([
                        dbc.Label('Model Selection for Risk Index'),
                        dcc.Dropdown(id='model-dropdown', placeholder="Select a model"),
                        dbc.Button("Submit", id='submit-button', color='info', className='mt-3')
                    ])
                ], style=dict(marginLeft=50, marginTop=100))
            ], width='40%'),


            html.Div([
                html.Iframe(id='iframe', srcDoc= open("./tmp_map/tmp_map_object.html", "r").read(), width="100%", height="800"), 
            ], style=dict(marginLeft= 100, marginTop=20, marginBottom=20, width=1200))

        ]), fluid=True 
    ),


    html.Div([
        html.Footer("@2019 Plant Pathology Lab    Oregon State University Hermiston Agriculture Research Center.    Contact: lixiaopi@oregonstate.edu")
    ])

    ]
)






@app.callback(
    Output('model-dropdown', 'options'),
    [Input('date-picker', 'date'),
    Input('outbreak', 'value'), 
    Input('model-dropdown', 'value')])
def update_model(pick_date, outbreak, model_selection):
    """
        if pick_date is first of June, model 1 is made available
        if pick_date passes August 31, and no late blight is observed
        then model 2 is made available
    """

    options = [{'label': 'Models is not available', 'value': 'NA'}]

    if pick_date is not None:

        date = dt.datetime.strptime(pick_date, "%Y-%m-%d")
        Month = date.month
        Year = date.year

        # archive data
        if Year in years and Year < today_year:

            if outbreak == 0:
                options = [
                    {'label':'Discriminate Func 1', 'value':'DFunc1'},
                    {'label': 'Discriminate Func 2', 'value': 'DFunc2'},
                    {'label': 'Logistic model 1', 'value':'LRM1'},
                    {'label': 'Logistic model 2', 'value':'LRM2'}
                ]
            elif outbreak == 1:

                options = [
                    {'label':'Discriminate Func 1', 'value':'DFunc1'},
                    {'label': 'Discriminate Func 2', 'value': 'DFunc2', 'disabled': True},
                    {'label': 'Logistic model 1', 'value':'LRM1'},
                    {'label': 'Logistic model 2', 'value':'LRM2', 'disabled': True}
                ]
        # current data
        elif Year in years and Year == today_year:

            if Month > 6 and Month <= 8:

                options = [
                    {'label':'Discriminate Func 1', 'value':'DFunc1'},
                    {'label': 'Discriminate Func 2', 'value': 'DFunc2', 'disabled': True},
                    {'label': 'Logistic model 1', 'value':'LRM1'},
                    {'label': 'Logistic model 2', 'value':'LRM2', 'disabled': True}
                ]

            # no out break
            elif Month > 8 and outbreak == 0:

                options = [
                    {'label':'Discriminate Func 1', 'value':'DFunc1'},
                    {'label': 'Discriminate Func 2', 'value': 'DFunc2', 'disabled': False},
                    {'label': 'Logistic model 1', 'value':'LRM1'},
                    {'label': 'Logistic model 2', 'value':'LRM2', 'disabled': False}
                ]

            # have outbreak
            elif Month > 8 and outbreak == 1:
                
                options = [
                    {'label':'Discriminate Func 1', 'value':'DFunc1'},
                    {'label': 'Discriminate Func 2', 'value': 'DFunc2', 'disabled': True},
                    {'label': 'Logistic model 1', 'value':'LRM1'},
                    {'label': 'Logistic model 2', 'value':'LRM2', 'disabled': True}
                ]

        elif Year not in years:
            options = [{'label': 'Models is not available', 'value': 'NA'}]

    else:
        options = [{'label': 'Models is not available', 'value': 'NA'}]


    return options




@app.callback( 
    Output('iframe', 'srcDoc'),
    [Input('submit-button', 'n_clicks')],
    [State('zipcode-input', 'value'),
    State('date-picker', 'date'), 
    State('interp-select', 'value'),
    State('model-dropdown', 'value'), 
    State('outbreak', 'value'),
    State('outbreak_prev', 'value')])
def update_graph(n_clicks, zipcodes, pick_date, interp, model_dropdown, outbreak, outbreak_prev):


    # # get zip to coords

    if zipcodes is not None:
        zipcoder = ZipcodeConvert(zipcodepath)
        zip2coords = zipcoder.zipcode_to_coords(zipcodes)
        zip2coords_list = list(zip2coords)

    if pick_date is not None:
        date = dt.datetime.strptime(pick_date, "%Y-%m-%d")
        # Month = date.month
        Year = date.year

        # load data frame byear
        if Year in years:


            df_byear = fetchall[fetchall['Year'] == Year]

        
            # all sites
            df_byear_copy = df_byear.copy()

            Pm_all = df_byear_copy['Pm'].values.tolist()
            Ram_all = df_byear_copy['Ram'].values.tolist()
            Rja_all = df_byear_copy['Rja'].values.tolist()

            # all sites
            # function 1
            DFun_one_all = [ riskmodels.johnson_determinant_fun1(Ram_all[i], Pm_all[i], False) for i in range(len(df_byear)) ]
            # functon 2
            DFun_two_all = [ riskmodels.johnson_determinant_fun2(Ram_all[i], Rja_all[i], False) for i in range(len(df_byear)) ]
            # logist_1
            Logistic_one_all = [ riskmodels.johnson_logist_model1(Ram_all[i], Pm_all[i], False) for i in range(len(df_byear)) ]
            # logist_2
            Logistic_two_all = [ riskmodels.johnson_logist_model2(Ram_all[i], Rja_all[i], False) for i in range(len(df_byear)) ]
            # add heat map
            data_array = np.array(list(zip(df_byear['Lat'], df_byear['Lon'], Logistic_one_all)))

            mapobject.add_heatmap(data=data_array)
            mapobject.savemap()

            # nearest top 10 sites
            distance = geomethods.picknearest10(df_byear, zip2coords_list)
            index = [ i['index'] for i in distance]
            # filter df_byear by distance {'index': index, 'dist':dist}
            filtered_df_0 = df_byear.iloc[index]
            filtered_df = filtered_df_0.reset_index()

            # calculate riskmodels values
            ref_points = np.array( list(zip(filtered_df['Lat'], filtered_df['Lon'])) )
            Pm = filtered_df['Pm']
            Ram = filtered_df['Ram'].astype(dtype=float)
            Rja = filtered_df['Rja'].astype(dtype=float)
            # interpolate values
            Pm_inter = geomethods.useInterpolate(ref_points, Pm, zip2coords_list, method=interp)
            Ram_inter = geomethods.useInterpolate(ref_points, Ram, zip2coords_list, method=interp)
            Rja_inter = geomethods.useInterpolate(ref_points, Rja, zip2coords_list, method=interp)


            # User location
            DFun_one = None
            DFun_two = None
            Logistic_one = None
            Logistic_two = None

            outbreakyear = "Your location is in outbreak year"
            nooutbreakyear = "Your location is NOT in outbreak year"
            # models
            if model_dropdown == 'DFun1':
                if outbreak_prev == 0:
                    DFun_one = riskmodels.johnson_determinant_fun1(Ram_inter, Pm_inter, False)
                    # add to map
                    if DFun_one:
                        mapobject.add_marker(zip2coords_list, outbreakyear)
                    else:
                        mapobject.add_marker(zip2coords_list, nooutbreakyear)

                    mapobject.savemap()

                else:
                    DFun_one = riskmodels.johnson_determinant_fun1(Ram_inter, Pm_inter, True)
                                        # add to map
                    if DFun_one:
                        mapobject.add_marker(zip2coords_list, outbreakyear)
                    else:
                        mapobject.add_marker(zip2coords_list, nooutbreakyear)

                    mapobject.savemap()

            elif model_dropdown == 'DFun2':

                if outbreak_prev == 0:
                    DFun_two = riskmodels.johnson_determinant_fun2(Ram_inter, Rja_inter, False)
                    # add to map
                    if DFun_two:
                        mapobject.add_marker(zip2coords_list, outbreakyear)
                    else:
                        mapobject.add_marker(zip2coords_list, nooutbreakyear)

                    mapobject.savemap()

                else:
                    DFun_two = riskmodels.johnson_determinant_fun2(Ram_inter, Rja_inter, True)
                    # add to map
                    if DFun_two:
                        mapobject.add_marker(zip2coords_list,outbreakyear)
                    else:
                        mapobject.add_marker(zip2coords_list, nooutbreakyear)

                    mapobject.savemap()

            elif model_dropdown == 'LRM1':

                if outbreak_prev == 0:
                    Logistic_one = riskmodels.johnson_logist_model1(
                        Ram_inter, Pm_inter, False
                    )
                    if Logistic_one >= 0.5:
                        mapobject.add_marker(zip2coords_list, outbreakyear)
                    else:
                        mapobject.add_marker(zip2coords_list, nooutbreakyear)


                    mapobject.savemap()

                else:
                    Logistic_one = riskmodels.johnson_logist_model1(
                        Ram_inter, Pm_inter, True
                    )

                    if Logistic_one >= 0.5:
                        mapobject.add_marker(zip2coords_list, outbreakyear)
                    else:
                        mapobject.add_marker(zip2coords_list, nooutbreakyear)

                    mapobject.savemap()

            elif model_dropdown == 'LRM2':

                if outbreak_prev == 0:
                    Logistic_two = riskmodels.johnson_logist_model2(
                        Ram_inter, Pm_inter, False
                    )

                    if Logistic_two >= 0.5:
                        mapobject.add_marker(zip2coords_list, outbreakyear)
                    else:
                        mapobject.add_marker(zip2coords_list, nooutbreakyear)

                    mapobject.savemap()

                else:
                    Logistic_two = riskmodels.johnson_logist_model2(
                        Ram_inter, Pm_inter, True
                    )
                    if Logistic_two >= 0.5:
                        mapobject.add_marker(zip2coords_list,outbreakyear)
                    else:
                        mapobject.add_marker(zip2coords_list,nooutbreakyear)

                    mapobject.savemap()
    
    src = open("./tmp_map/tmp_map_object.html", 'r').read()

    return src

if __name__ == '__main__':
    app.run_server()