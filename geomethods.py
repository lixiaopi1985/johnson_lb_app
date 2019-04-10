"""
This function is used to interpolate risk facts
"""
import numpy as np
from math import radians, sin, cos, atan2,sqrt
from scipy import interpolate as Interp
from geopy.distance import geodesic
import pykrige.kriging_tools as kt
from pykrige.ok import OrdinaryKriging



class InterpolationMethods:
    """uses scipy interploate NeareastNDInterpolator.
    Turn coordinates decimal to radians
    
    Arguments:
        ref_coord_value: {ndarray} -- array([[x, y, value]])
        query_point {list or array} -- coordinates to interpolate
    """

    def __init__(self, ref_df, query_point, properties):
        self.ref_df = ref_df
        self.query_point = query_point
        self.properties = properties

    @staticmethod
    def df2array(df, properties):
        """[summary]
        
        Arguments:
            properties {column names} -- eg: [latitude,longitude,PP]

        Returns:
            ndarray
        """
        assert type(properties) == list, "Properties is a list"
        ref_coord_value = df.loc[:, properties].values
        return ref_coord_value



    def generateCoordValues(self):
        self.ref_coord_value = InterpolationMethods.df2array(self.ref_df, self.properties)
        return self

    def picknearestN(self, N=-1):
        """[summary]
        
        Arguments:
            N: top values to return, default: whole
        
        Returns:
            tuple of lists: index, distance
        """

        coords = list(zip(self.ref_coord_value[:, 0], self.ref_coord_value[:, 1])) #(lat, long)
        dist = [ {'index': index, 'dist': geodesic(self.query_point, val).miles } for index, val in enumerate(coords) ]
        dist_c = dist[:]
        # pick the nearest 10
        dist_c.sort(key=lambda x: x['dist'])
        topN = dist_c[0:N]

        self.index = [ i['index'] for i in topN]
        self.dist_N = [ i['dist'] for i in topN]
        self.topDF = self.ref_df.loc[self.index, self.properties]

        return self


    def NND(self):
        coord_value = InterpolationMethods.df2array(self.topDF, self.properties)
        ref_p_radian = np.array(list(map(lambda x: (radians(x[0]), radians(x[1])), coord_value)))
        ref_values = np.array(coord_value[:, 2])
        interp_array = Interp.NearestNDInterpolator(ref_p_radian, ref_values)
        result = interp_array(self.query_point)

        return round(float(result), 2)


    def IWD(self, power=2):


        distance = np.array(self.dist_N)
        known_values = self.topDF.values[:, 2]

        powered_distance = np.power(distance, power)
        numerator = np.sum( known_values / powered_distance )
        denominator = np.sum( 1.0 / powered_distance )
        result = numerator / denominator
        return round(result, 2)


    def radicalFunc(self, fun='gaussian'):

        """
        see https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.Rbf.html
        """
        mtx = self.topDF.values

        rbfi = Interp.Rbf(mtx[:, 0], mtx[:, 1], mtx[:, 2], fun=fun)

        di = rbfi(self.query_point[0], self.query_point[1])

        return round(float(di), 2)


    def kriging(self, type='Ordinary', variogram_model='gaussian', intertype="points"):
        """https://buildmedia.readthedocs.org/media/pdf/pykrige/latest/pykrige.pdf"""
        mtx = self.topDF.values
        OK = OrdinaryKriging(mtx[:, 0], mtx[:, 1], mtx[:, 2], variogram_model = variogram_model, verbose=False, enable_plotting=False)
        z, _ = OK.execute(intertype, self.query_point[0], self.query_point[1])

        return round(float(z),2)


    def pickMethods(self, methods="IDW"):

        result = None
        if methods == "IDW":
            result = self.IWD()

        elif methods == "NND":
            result = self.NND()

        elif methods == "Radical":
            result = self.radicalFunc()

        elif methods == 'Krig':
            result = self.kriging()

        else:
            raise ValueError("No such methods")

        return result
        
