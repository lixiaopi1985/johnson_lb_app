"""
This function is used to interpolate risk facts
"""
import numpy as np
from math import radians, sin, cos, atan2,sqrt
from scipy import interpolate as Interp
from geopy.distance import geodesic



# def geoCoordsDistance(pos1, pos2):
#     """uses 'havesine' formula

#     havesine: a = sin(delta_lat/2)**2 + cos(lat1)cos(lat2)*(sin(delta_lon/2)**2)

#               c = 2* atan2(sqrt(a), sqrt(1-a))

#               d = R*c
    
#     Arguments:
#         pos1 tuple or list or np array -- place 1 coordinate (45.555, -112.2200)
#         pos2 tuple or list or np array -- place 2 coordinate (45.555, -112.2200)

#     return distance in miles
#     """

#     R = 3958.8 # miles earth radius 6371e3 km

#     lat1 = radians(pos1[0]); lon1 = radians(pos1[1])
#     lat2 = radians(pos2[0]); lon2 = radians(pos2[1])

#     delta_lat = lat2 - lat1
#     delta_lon = lon2 - lon1

    
#     a = sin(delta_lat/2)**2 + cos(lat1)*cos(lat2)*(sin(delta_lon/2)**2)

#     c = 2*atan2(sqrt(a), sqrt(1-a))

#     return R*c





def picknearest10(ref_df, query_points):
    """[summary]
    
    Arguments:
        ref_df {[type]} -- [description]
        query_points {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """

    coords = list(zip(ref_df['Lat'], ref_df['Lon']))
    dist = [ {'index': index, 'dist': geodesic(query_points, val).miles } for index, val in enumerate(coords) ]

    dist_c = dist[:]
    # pick the nearest 10
    dist_c.sort(key=lambda x: x['dist'])

    return dist_c[0:10]


def useInterpolate(ref_points, ref_values, query_point, method = 'NND'):
    """uses scipy interploate NeareastNDInterpolator.
    Turn coordinates decimal to radians
    
    Arguments:
        ref_points {array of coordinates} -- np.array([x, y])
        ref_values {array of values} -- np.array([pm])
        query_point {list or array} -- coordinates to interpolate
        method {string} -- method to use to interpolate: NND, LND
    """

    ref_p_radian = np.array(list(map(lambda x: (radians(x[0]), radians(x[1])), ref_points)))

    ref_values = np.array(ref_values)

    interp_array = Interp.NearestNDInterpolator(ref_p_radian, ref_values)

    if method == 'LND':
        interp_array = Interp.LinearNDInterpolator(ref_p_radian, ref_values)


    return interp_array(query_point)








    










def geoCoordsEstimator():
    """
    barycentric coordinates
    """
