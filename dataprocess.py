"""This module is used to connect to database and build models
"""
import pandas as  pd
import sqlite3
import sys
import datetime as dt
import converters
import numpy as np
import re
import datetime as t
import json
import riskmodels


def daterange(dbpath, dbtable, dformat="%Y-%m-%d"):

    try:
        conn = sqlite3.connect(dbpath)
    except sqlite3.DatabaseError as e:
        print(e)
        sys.exit(1)

    cur = conn.cursor()
    getcols = f"""PRAGMA table_info ({dbtable});"""
    cur.execute(getcols)
    col_tuples = cur.fetchall()
    cols = [ i[1] for i in col_tuples ]

    datecol = getCol(cols, 'Datetime')


    sql_select_date = f"""SELECT {datecol} FROM {dbtable};"""
    cur.execute(sql_select_date)

    date_all = cur.fetchall()

    date_list = [ dt.datetime.strptime(i[0], dformat) for i in date_all]

    return min(date_list), max(date_list)



def getCol(collist, key):
    """Decides column types to store for database
    
    Arguments:
        df {pandas dataframe} -- [pandas dataframe]
    """
    # cols = df.columns.tolist()


    coltypes = {
        'Datetime':r"^[Dd]ate.*?$|^DATE.*?$|[Yy]ear.*?$|^YEAR.*?$|^[Tt]ime$|^[Dd]ay.*?$|^[Mm]onth.*?$|^MONTH.*?$",
        'Site':r"[Ss]ite.*|SITE.*",
        'Description':r"^[Dd]escription.*?$|^DESCRIPTION$",
        'Floats': r"^[Ll]atitude$|^LATITUDE$|^[Ll]ongitude$|^LONGITUDE$|^ELEVATION.*?$|^[Ee]levation.*?$|^[A-Za-z]{2,4}$|^[A-Za-z]{2}[0-9]{1}$"

    }

    # compile pattern
    regex = re.compile(coltypes[key])

    col = []
    for i in collist:
        if regex.search(i):
            col.append(i)


    return ",".join(col)




class DataAggregate:

    def __init__(self, dbpath, dbtable, metatable, inputdate):
        self.dbpath = dbpath
        self.dbtable = dbtable
        self.metatable = metatable
        self.inputdate = inputdate


    def getData(self):

        try:
            conn = sqlite3.connect(self.dbpath)
        except sqlite3.DatabaseError:
            print(sqlite3.DatabaseError, file=sys.stderr)
            sys.exit(1)

        cur = conn.cursor()
        getcols = f"""PRAGMA table_info ({self.dbtable});"""
        cur.execute(getcols)
        col_tuples = cur.fetchall()
        cols = [ i[1] for i in col_tuples ]
        
        # get meta data
        metadata_sql = f"SELECT * FROM {self.metatable};"
        meta_df = pd.read_sql_query(metadata_sql, conn)

        getcols = f"""PRAGMA table_info ({self.metatable});"""
        cur.execute(getcols)
        meta_col_tuples = cur.fetchall()
        meta_cols = [ i[1] for i in meta_col_tuples ]
        meta_site_col = getCol(meta_cols, 'Site')
        


        # to dataframe
        datecol = getCol(cols, 'Datetime')

        dt_object = dt.datetime.strptime(self.inputdate, "%Y-%m-%d")
        Year = dt_object.year
        sql = f"""SELECT * FROM {self.dbtable} WHERE {datecol} LIKE '{Year}-%';"""

        df = pd.read_sql_query(sql, conn, parse_dates=[datecol])
        

        # RAM
        # RJA
        # PM
        # all we need is minimum temperature (in C) and rainfall (in mm)

        # select MN and PP

        sitecol = getCol(cols, 'Site')
        paramcols = getCol(cols, 'Floats').split(",")


        try:
            df_filtered = df.loc[:, [datecol, sitecol] + [i for i in paramcols if i == "MN" or i == "PP"]]

        except:
            print("Error occured during filtering", file=sys.stderr)
            sys.exit(1)

        
        # merge with meta data
        df_filtered.replace("NA", np.nan, inplace=True)

        # convert unites
        df_filtered.fillna(method='backfill', inplace=True) # might have to fill with other data
        df_filtered["PP"] = df_filtered["PP"].apply(converters.LengthConverter)
        df_filtered["MN"] = df_filtered["MN"].apply(converters.TemperatureConverter)


        # RAM: Number of days with rain >= 0.25nm during April and May
        # RJA: Number of days with rain >=0.25nm during July and August
        # PM: Total precipitation during May when daily minimum temperature was greater or equal to 5C
        df_filtered['RAM'] = 1
        df_filtered["RJA"] = 1
        
        df_filtered["Year"] = df_filtered[datecol].apply(lambda x: x.year)
        df_filtered["Month"] = df_filtered[datecol].apply(lambda x: x.month)


        # 4 and 5 where PP >= 0.25
        df_am = df_filtered[(df_filtered["Month"] == 4) | (df_filtered["Month"] == 5)]
        df_ram = df_am[df_am["PP"] >= 0.25]
        # July and August
        df_ja = df_filtered[(df_filtered["Month"] == 7) | (df_filtered["Month"] == 8)]
        df_rja = df_ja[df_ja["PP"] >= 0.25]
 
        # groupby sites
        df_ram_sites = df_ram.groupby(by=[sitecol]).aggregate({'RAM':'count'})
        df_rja_sites = df_rja.groupby(by=[sitecol]).aggregate({'RJA':'count'})

        #PM
        df_may = df_filtered[df_filtered["Month"] == 5]
        df_pm_c = df_may[df_may['MN'] >=5]
        df_pm = df_pm_c.groupby([sitecol]).aggregate({"PP":"sum"})

        df_out = pd.concat([df_ram_sites, df_rja_sites, df_pm], axis=1, sort=False, join="inner")
        df_out.reset_index(inplace=True)

        self.df_clean = df_out.merge(meta_df, left_on=sitecol, right_on=meta_site_col, how='inner')

        return self.df_clean



class ModelAggregate(DataAggregate):

    def __init__(self, selectedmodel, Yp, **kwargs):
        super().__init__(**kwargs)
        self.selectedmodel = selectedmodel
        self.Yp = Yp


    def calcModel(self):

        self.df = super().getData()

        if self.selectedmodel == "log1":

            for i, row in self.df.iterrows():
                ram = row['RAM']
                pm = row['PP']
                p = riskmodels.johnson_logist_model1(ram, pm, self.Yp)
                self.df.loc[i, 'pval'] = p 


        if self.selectedmodel == "log2":


            for i, row in self.df.iterrows():
                ram = row['RAM']
                rja = row['RJA']
                p = riskmodels.johnson_logist_model2(ram, rja, self.Yp)
                self.df.loc[i, 'pval'] = p 


        return self

    def df_to_geojson(self, properties, lat='latitude', lon='longitude', dumppath="./static/weather.geojson"):

        geojson = {'type':'FeatureCollection', 'features':[]}

        for _, row in self.df.iterrows():

            # create a feature template to fill in
            feature = {
                'type':'Feature',
                'properties':{},
                'geometry':{
                    'type':'Point',
                    'coordinates':[]
                }
            }

            feature['geometry']['coordinates'] = [row[lon],row[lat]]

            for prop in properties:
                feature['properties'][prop] = row[prop]

            geojson['features'].append(feature)

        with open(dumppath, 'w') as f:
            return json.dump(geojson, f)

    def getDataframe(self):
        return self.df




class EstimateModel:

    def __init__(self, e_ram, e_rja, e_pp, Yp):
        self.e_ram = e_ram
        self.e_rja = e_rja
        self.e_pp = e_pp
        self.Yp = Yp


    def estimatePoint(self, model):
        riskp = None
        if model == "log1":
            riskp = riskmodels.johnson_logist_model1(self.e_ram, self.e_pp, self.Yp)
        elif model == 'log2':
            riskp = riskmodels.johnson_logist_model2(self.e_ram, self.e_rja, self.Yp)
        else:
            raise ValueError("No such model")

        return round(riskp, 2)


