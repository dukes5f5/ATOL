"""
Simple Geodetic Distance Calculator
===================================

A simplified Python script that calculates geographic distances using rhumb line 
or great circle methods with ellipsoid support, emulating MATLAB's distance function.

Uses only basic Python functions - no classes needed!
"""

import math
import numpy as np

# Ellipsoid definitions (semi-major axis in meters, flattening)
ELLIPSOIDS = {
    'WGS84': {'a': 6378137.0, 'f': 1/298.257223563},
    'GRS80': {'a': 6378137.0, 'f': 1/298.257222101},
    'Clarke1866': {'a': 6378206.4, 'f': 1/294.978698214},
    'Bessel1841': {'a': 6377397.155, 'f': 1/299.1528128},
    'Airy1830': {'a': 6377563.396, 'f': 1/299.3249646},
    'International1924': {'a': 6378388.0, 'f': 1/297.0},
    'Krassowsky1940': {'a': 6378245.0, 'f': 1/298.3},
    'NAD83': {'a': 6378137.0, 'f': 1/298.257222101},
    'sphere': {'a': 6371000.0, 'f': 0.0}
}

def distance(pt1, pt2, ellipsoid='WGS84', method='great_circle', back_az=False):
    """
    Calculate distance and azimuth between two geographic points.
    
    This function emulates MATLAB's distance function with simple keyword arguments.
    
    Args:
        pt1: First point as (latitude, longitude) in degrees
        pt2: Second point as (latitude, longitude) in degrees
        ellipsoid: Ellipsoid name - 'WGS84', 'GRS80', etc. (default: 'WGS84')
        method: 'great_circle' or 'rhumb' (default: 'great_circle')
        back_az: If True, return back azimuth instead of forward (default: False)
    
    Returns:
        Tuple of (azimuth_degrees, distance_meters) both rounded to 2 decimal places
        Azimuth is normalized to 0-359.99 degrees
    
    Examples:
        >>> # Basic usage
        >>> az, dist = distance((40.7128, -74.0060), (51.5074, -0.1278))
        
        >>> # Rhumb line with different ellipsoid
        >>> az, dist = distance(pt1, pt2, ellipsoid='GRS80', method='rhumb')
        
        >>> # Get back azimuth
        >>> back_az, dist = distance(pt1, pt2, back_az=True)
    """
    
    # Get coordinates
    lat1, lon1 = pt1
    lat2, lon2 = pt2
    
    # Validate coordinates
    if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees")
    
    # Get ellipsoid parameters
    if ellipsoid not in ELLIPSOIDS:
        available = ', '.join(ELLIPSOIDS.keys())
        raise ValueError(f"Unknown ellipsoid '{ellipsoid}'. Available: {available}")
    
    # Validate method
    if method not in ['great_circle', 'rhumb']:
        raise ValueError("Method must be 'great_circle' or 'rhumb'")
    
    # Get ellipsoid parameters
    ell = ELLIPSOIDS[ellipsoid]
    a = ell['a']  # Semi-major axis
    f = ell['f']  # Flattening
    b = a * (1 - f)  # Semi-minor axis
    e = math.sqrt(2 * f - f**2)  # First eccentricity
    
    # Calculate based on method
    if method == 'great_circle':
        azimuth, dist = _great_circle_distance(lat1, lon1, lat2, lon2, a, b, f, back_az)
    else:  # rhumb
        azimuth, dist = _rhumb_line_distance(lat1, lon1, lat2, lon2, a, e, back_az)
    
    # Round to 2 decimal places
    azimuth = round(azimuth, 2)
    dist = round(dist, 2)
    
    return (azimuth, dist)

def _great_circle_distance(lat1, lon1, lat2, lon2, a, b, f, back_az):
    """Calculate great circle distance using Vincenty's formula."""
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Check if points are the same
    if abs(lat1 - lat2) < 1e-10 and abs(lon1 - lon2) < 1e-10:
        return (0.0, 0.0)
    
    # Vincenty's formula
    L = lon2_rad - lon1_rad
    U1 = math.atan((1 - f) * math.tan(lat1_rad))
    U2 = math.atan((1 - f) * math.tan(lat2_rad))
    sin_U1 = math.sin(U1)
    cos_U1 = math.cos(U1)
    sin_U2 = math.sin(U2)
    cos_U2 = math.cos(U2)
    
    lambda_val = L
    lambda_prev = 2 * math.pi
    iter_limit = 100
    
    # Initialize variables
    sin_sigma = 0
    cos_sigma = 0
    sigma = 0
    sin_alpha = 0
    cos2_alpha = 0
    cos_2sigma_m = 0
    sin_lambda = 0
    cos_lambda = 0
    
    while abs(lambda_val - lambda_prev) > 1e-12 and iter_limit > 0:
        sin_lambda = math.sin(lambda_val)
        cos_lambda = math.cos(lambda_val)
        
        sin_sigma = math.sqrt((cos_U2 * sin_lambda) ** 2 + 
                             (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2)
        
        if sin_sigma == 0:
            return (0.0, 0.0)  # Co-incident points
        
        cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        
        sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
        cos2_alpha = 1 - sin_alpha ** 2
        
        if cos2_alpha == 0:
            cos_2sigma_m = 0  # Equatorial line
        else:
            cos_2sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha
        
        C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
        
        lambda_prev = lambda_val
        lambda_val = L + (1 - C) * f * sin_alpha * (
            sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * 
                                   (-1 + 2 * cos_2sigma_m ** 2)))
        
        iter_limit -= 1
    
    if iter_limit == 0:
        # For antipodal points, use simple approximation
        if abs(abs(lat1) + abs(lat2) - 180) < 1e-6:
            distance = math.pi * a
            azimuth_deg = 90.0 if lon2 > lon1 else 270.0
            return (azimuth_deg, distance)
        else:
            raise ValueError("Great circle calculation failed to converge")
    
    # Calculate distance
    u2 = cos2_alpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    
    delta_sigma = B * sin_sigma * (cos_2sigma_m + B / 4 * (cos_sigma * 
                 (-1 + 2 * cos_2sigma_m ** 2) - B / 6 * cos_2sigma_m * 
                 (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigma_m ** 2)))
    
    distance = b * A * (sigma - delta_sigma)
    
    # Calculate azimuth
    azimuth_rad = math.atan2(cos_U2 * sin_lambda, 
                            cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda)
    
    # Calculate back azimuth if requested
    if back_az:
        back_azimuth_rad = math.atan2(cos_U1 * sin_lambda,
                                     -sin_U1 * cos_U2 + cos_U1 * sin_U2 * cos_lambda)
        azimuth_rad = back_azimuth_rad
    
    azimuth_deg = _normalize_azimuth(math.degrees(azimuth_rad))
    
    return (azimuth_deg, distance)

def _rhumb_line_distance(lat1, lon1, lat2, lon2, a, e, back_az):
    """Calculate rhumb line distance and azimuth."""
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Check if points are the same
    if abs(lat1 - lat2) < 1e-10 and abs(lon1 - lon2) < 1e-10:
        return (0.0, 0.0)
    
    # Calculate difference in longitude
    dlon = lon2_rad - lon1_rad
    
    # Normalize longitude difference
    if abs(dlon) > math.pi:
        if dlon > 0:
            dlon = -(2 * math.pi - dlon)
        else:
            dlon = 2 * math.pi + dlon
    
    # Calculate isometric latitude
    def isometric_latitude(lat):
        if abs(lat) > math.pi/2 - 1e-10:
            return float('inf') if lat > 0 else float('-inf')
        
        esin_lat = e * math.sin(lat)
        return math.log(math.tan(math.pi/4 + lat/2) * 
                       ((1 - esin_lat) / (1 + esin_lat)) ** (e/2))
    
    psi1 = isometric_latitude(lat1_rad)
    psi2 = isometric_latitude(lat2_rad)
    dpsi = psi2 - psi1
    
    # Calculate azimuth
    if abs(dpsi) < 1e-10:
        # East-west line
        azimuth_rad = math.pi/2 if dlon > 0 else -math.pi/2
    else:
        azimuth_rad = math.atan2(dlon, dpsi)
    
    azimuth_deg = _normalize_azimuth(math.degrees(azimuth_rad))
    
    # Calculate back azimuth if requested
    if back_az:
        azimuth_deg = _normalize_azimuth(azimuth_deg + 180.0)
    
    # Calculate distance
    if abs(lat1_rad - lat2_rad) < 1e-10:
        # East-west line
        distance = a * math.cos(lat1_rad) * abs(dlon) / math.sqrt(1 - e**2 * math.sin(lat1_rad)**2)
    else:
        # General case
        if abs(dpsi) < 1e-10:
            # North-south line
            distance = a * (1 - e**2) * abs(lat2_rad - lat1_rad) / \
                      (1 - e**2 * math.sin((lat1_rad + lat2_rad)/2)**2)**1.5
        else:
            # General rhumb line
            distance = abs(dpsi) * a * math.sqrt(1 - e**2 * math.sin((lat1_rad + lat2_rad)/2)**2) / \
                      abs(math.cos(azimuth_rad))
    
    return (azimuth_deg, distance)

def _normalize_azimuth(azimuth_deg):
    """Normalize azimuth to 0-359.99 degrees."""
    normalized = azimuth_deg % 360.0
    if normalized >= 360.0:
        normalized = 0.0
    return normalized

def get_available_ellipsoids():
    """Get list of available ellipsoid names."""
    return list(ELLIPSOIDS.keys())

# pt1 =  (36.07365833, -115.125825)
# pt2 = (36.07362778, -115.1614333)

# result = distance(pt1, pt2, ellipsoid='WGS84', method='great_circle', back_az=False)
# print(result)

