import numpy as np

def fun_sinusoid(points):
    """
    Slowly varying standard sinusoid over the globe
    :param points: evaluation points
    :return: function at points
    """
    xcoord = points[:, 0]
    ycoord = points[:, 1]
    conv = np.pi / 180.0
    length = 1.2 * np.pi
    coef = 2.
    coefmult = 1.
    evaluated = coefmult * (coef - np.cos(np.pi*(np.arccos(np.cos(xcoord * conv) * np.cos(ycoord * conv))/length)))
    return evaluated

def fun_harmonic(points):
    """
    More rapidly varying function with 16 maximums and 16 minimums in
    northern and southern bands
    :param points: evaluation points
    :return: function at points
    """
    xcoord = points[:, 0]
    ycoord = points[:, 1]
    conv = np.pi / 180.0
    evaluated = 2.0 + np.sin(2.0 * ycoord * conv) ** 16.0 * np.cos(16.0 * xcoord * conv)
    return evaluated

def fun_vortex(points):
    """
    Slowly varying function with two added vortices, one in the Atlantic and
    one over Indonesia
    :param points: evaluation points
    :return: function at points
    """
    xcoord = points[:, 0]
    ycoord = points[:, 1]
    conv = np.pi / 180.0
    lon0 = 5.5
    lat0 = 0.2
    R0 = 3.0
    D = 5.0
    T = 6.0
    sinC = np.sin(lat0)
    cosC = np.cos(lat0)

    cosT = np.cos(ycoord * conv)
    sinT = np.sin(ycoord * conv)
    trm = cosT * np.cos(xcoord * conv - lon0)
    X = sinC * trm - cosC * sinT
    Y = cosT * np.sin(xcoord * conv - lon0)
    Z = sinC * sinT + cosC * trm
    lon = np.arctan2(Y, X)
    lon[lon < 0.0] += 2.0 * np.pi
    lat = np.arcsin(Z)

    rho = R0 * np.cos(lat)
    vt = 3.0 * np.sqrt(3.0)/2.0/np.cosh(rho)/np.cosh(rho)*np.tanh(rho)
    omega = np.zeros_like(rho)
    rho_idx = rho != 0.0
    omega[rho_idx] = vt[rho_idx] / rho[rho_idx]

    evaluated = 2.0 * (1.0 + np.tanh(rho / D * np.sin(lon - omega * T)))
    return evaluated

def fun_gulfstream(points, offset=1):
    """
    Slowly varying standard sinusoid with a mimicked Gulf Stream.
    :param points: evaluation points
    :param offset: offsets output to avoid 0 values
    :return: function at points
    """
    xcoord = points[:, 0]
    ycoord = points[:, 1]
    conv = np.pi / 180.0
    length = 1.2 * np.pi
    coef = 1.0
    ori_lon = -80.0
    ori_lat = 25.0
    end_lon = -1.8
    end_lat = 50.0
    dmp_lon = -25.5
    dmp_lat = 55.5
    dr0 = np.sqrt(((end_lon-ori_lon)*conv)**2 + ((end_lat-ori_lat)*conv)**2)
    dr1 = np.sqrt(((dmp_lon-ori_lon)*conv)**2 + ((dmp_lat-ori_lat)*conv)**2)

    evaluated = (coef - np.cos(np.pi*(np.arccos(np.cos(ycoord*conv)*np.cos(xcoord*conv))/length)))
    per_lon = xcoord
    per_lon[per_lon > 180.0] -= 360.0
    per_lon[per_lon < -180.0] += 360.0
    dx = (per_lon - ori_lon) * conv
    dy = (ycoord - ori_lat) * conv
    dr = np.sqrt(dx*dx + dy*dy)
    dth = np.arctan2(dy, dx)
    dc = 1.3 * coef * np.ones_like(dr)
    dc[dr > dr0] = 0.0
    dc[dr > dr1] *= np.cos(np.pi*0.5*(dr[dr > dr1]-dr1)/(dr0-dr1))
    evaluated += (np.maximum(1000.0*np.sin(0.4*(0.5*dr+dth) + 0.007*np.cos(50.0*dth) + 0.37*np.pi), 999.0) - 999.0) * dc
    return evaluated + offset