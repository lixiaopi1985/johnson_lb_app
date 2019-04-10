import math
"""
reference: Johnson, D.A., Alldredge, J.R. and Vakoch, D.L. 1996. Potato Late Blight forecasting models for the\
    semiarid environment of south-central Washington. Phytopathology 86:486-484
"""

# def johnson_determinant_fun1(ram, pm, Yp=True):
#     """This is the first discriminant function used to predict outbreak and nonoutbreak years.
    
#     Arguments:
#         ram {float} -- Number of days with rain >= 0.25nm during April and May
#         pm {float} -- Total precipitation during May when daily minimum temperature was greater or equal to 5C
    
#     Keyword Arguments:
#         Yp {bool} -- lateblight outbreak duiring the preceding year (default: {True})
#     Returns:
#         A bool -- if it is an outbreak year or not an outbreak year.
#     """

#     try:
#         RAM = float(ram)
#         PM = float(pm)
#     except TypeError:
#         print("Input 'ram' and 'pm' should be numbers")
#         return

#     NonOutBreak = -4.426 + 0.863*RAM + 0.052*PM
#     OutBreak = -11.866 + 1.462*RAM - 0.033*PM

#     if Yp:
#         NonOutBreak += 2.052
#         OutBreak += 6.191

#     return OutBreak > NonOutBreak
    
# def johnson_determinant_fun2(ram, rja, Yp=True):
#     """This is the second discriminant function used to predict outbreak and nonoutbreak years.
#         You can only use this model: if no late blight has been observed by August 31
    
#     Arguments:
#         ram {float} -- Number of days with rain >= 0.25nm during April and May
#         rja {float} -- Number of days with rain >=0.25nm during July and August
    
#     Keyword Arguments:
#         Yp {bool} -- lateblight outbreak duiring the preceding year (default: {True})
#     Returns:
#         A bool -- if it is an outbreak year or not an outbreak year.
#     """

#     try:
#         RAM = float(ram)
#         RJA = float(rja)
#     except TypeError:
#         print("Input 'ram' and 'pm' should be numbers")
#         return

#     NonOutBreak = -5.636 + 0.974*RAM + 0.5*RJA
#     OutBreak = -14.546 + 1.506*RAM +0.711*RJA

#     if Yp:
#         NonOutBreak += 1.774
#         OutBreak += 5.776

#     return OutBreak > NonOutBreak



def johnson_logist_model1(ram, pm, Yp=True):
    """This is the 
    
    Arguments:
        ram {float} -- Number of days with rain >= 0.25nm during April and May
        pm {float} -- Total precipitation during May when daily minimum temperature was greater or equal to 5C
    
    Keyword Arguments:
        Yp {bool} -- lateblight outbreak duiring the preceding year (default: {True})
    
    Returns:
        float -- the probabilty of an outbreak.
    """


    try:
        RAM = float(ram)
        PM = float(pm)
    except TypeError:
        print("Input 'ram' and 'pm' should be numbers")
        return

    L = 7.548 - 0.629*RAM + 0.09*PM

    if Yp:
        L = L - 3.553

    P = 1/(1+math.exp(L))

    return P
    
def johnson_logist_model2(ram, rja, Yp=True):
    """This is the second model <logistic model> used to predict potato late blight outbreak.
    You can only use this model: if no late blight has been observed by August 31
    
    Arguments:
        ram {float} -- Number of days with rain >= 0.25nm during April and May
        rja {float} -- Number of days with rain >=0.25nm during July and August
    
    Keyword Arguments:
        Yp {bool} -- lateblight outbreak duiring the preceding year (default: {True})
    
    Returns:
        float -- the probabilty of an outbreak.
    """


    try:
        RAM = float(ram)
        RJA = float(rja)
    except TypeError:
        print("Input 'ram' and 'RJA' should be numbers")
        return

    L = 11.470 - 0.716*RAM - 0.259*RJA

    if Yp:
        L = L - 3.88

    P = 1/(1+math.exp(L))

    return float(P)


    

    