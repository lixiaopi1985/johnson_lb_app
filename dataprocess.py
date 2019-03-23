"""This module is used to connect to database and build models
"""
import pandas as  pd
import sqlite3


class ZipcodeConvert:

    def __init__(self, filepath):
        self.filepath = filepath

    def zipcode_to_coords(self, zipcode, mode='csv', sep=';'):

        assert zipcode != "", "zipcode should be numbers"
        zipcode = int(zipcode)

        if mode == 'csv':
            df = pd.read_csv(self.filepath, sep=sep)

        dff = df[df['Zip'] == zipcode]

        return float(dff['Latitude']), float(dff['Longitude'])

class Dbfetch:

    def __init__(self, dbpath):
        self.dbpath = dbpath

    def fetchAll(self, year=None):
        try:
            conn = sqlite3.connect(self.dbpath)
        except sqlite3.Error as e:
            print("Open Database Error")
            return e

        cur = conn.cursor()

        sql = """
        SELECT Pm.Years, 
                siteid, 
                description, 
                state, 
                latitude, 
                longitude,
                Pm.PP, 
                Rja.Rja, 
                Ram.Ram
        FROM Stations
            JOIN PmTable as Pm
                ON Stations.siteid = Pm.Sites
            JOIN RjaTable as Rja
                ON Stations.siteid = Rja.Sites
            JOIN RamTable as Ram
                ON Stations.siteid = Ram.Sites
        GROUP BY Pm.Years, siteid
        """

        if year:
            sql = """
            SELECT Pm.Years, 
                    siteid, 
                    description, 
                    state, 
                    latitude, 
                    longitude,
                    Pm.PP, 
                    Rja.Rja, 
                    Ram.Ram
            FROM Stations
                JOIN PmTable as Pm
                    ON Stations.siteid = Pm.Sites
                JOIN RjaTable as Rja
                    ON Station.siteid = Rja.Sites
                JOIN RamTable as Ram
                    ON Station.siteid = Ram.Sites
            WHERE Pm.Years = {}
            GROUP BY Pm.Years, siteid
            """.format(year)


        cur.execute(sql)
        self.all_info = cur.fetchall() # list contains tuples [ ( year, siteid, descript, state, lat, lon)]

        return self

    def Todataframe(self):
        '''construct dataframe
        '''

        if len(self.all_info) == 0:
            raise ValueError('Inquiry result is empty.')

        year = [ i[0] for i in self.all_info]
        siteid = [ i[1] for i in self.all_info]
        describe = [ i[2] for i in self.all_info]
        state = [i[3] for i in self.all_info]
        lat = [i[4] for i in self.all_info]
        lon =[i[5] for i in self.all_info]
        pm =[i[6] for i in self.all_info]
        rja =[i[7] for i in self.all_info]
        ram =[i[8] for i in self.all_info]


        df = pd.DataFrame({'Year': year, 'Siteid': siteid, 'Description': describe, 
                            'State': state, 'Lat': lat, 'Lon': lon, 'Pm': pm, 'Rja': rja, 'Ram': ram})

        return df


