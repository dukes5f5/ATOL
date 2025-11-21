"""
WGS84 Coordinate Generator

A standalone Python method for generating new coordinates using WGS84 standards
with support for both rhumb line and great circle ellipsoid calculations.

Uses only Anaconda 3 standard libraries (math, numpy).
"""

import math
import numpy as np


def generate_wgs84_coordinate(latitude, longitude, elevation, bearing, distance, 
                            method='great_circle'):
    """
    Generate a new WGS84 coordinate from a starting point using bearing and distance.
    
    Parameters:
    -----------
    latitude : float
        Starting latitude in decimal degrees (-90 to 90)
    longitude : float
        Starting longitude in decimal degrees (-180 to 180)
    elevation : float
        Starting elevation in meters
    bearing : float
        Bearing in degrees (0-360, where 0 is North, 90 is East)
    distance : float
        Distance in meters
    method : str, optional
        Calculation method: 'great_circle' or 'rhumb_line' (default: 'great_circle')
    
    Returns:
    --------
    tuple
        (new_latitude, new_longitude, new_elevation) in decimal degrees and meters
    
    Raises:
    -------
    ValueError
        If input parameters are out of valid ranges
    """
    
    # Input validation
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude must be between -90 and 90 degrees, got {latitude}")
    
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude must be between -180 and 180 degrees, got {longitude}")
    
    if not (0 <= bearing <= 360):
        raise ValueError(f"Bearing must be between 0 and 360 degrees, got {bearing}")
    
    if distance < 0:
        raise ValueError(f"Distance must be non-negative, got {distance}")
    
    if method not in ['great_circle', 'rhumb_line']:
        raise ValueError(f"Method must be 'great_circle' or 'rhumb_line', got {method}")
    
    # WGS84 ellipsoid parameters
    WGS84_A = 6378137.0  # Semi-major axis in meters
    WGS84_F = 1 / 298.257223563  # Flattening
    WGS84_B = WGS84_A * (1 - WGS84_F)  # Semi-minor axis
    WGS84_E2 = WGS84_F * (2 - WGS84_F)  # First eccentricity squared
    
    # Convert to radians
    lat1_rad = math.radians(latitude)
    lon1_rad = math.radians(longitude)
    bearing_rad = math.radians(bearing)
    
    if method == 'great_circle':
        # Great circle calculation using Vincenty's direct formula
        new_lat_rad, new_lon_rad = _vincenty_direct(
            lat1_rad, lon1_rad, bearing_rad, distance, WGS84_A, WGS84_F
        )
    else:  # rhumb_line
        # Rhumb line calculation
        new_lat_rad, new_lon_rad = _rhumb_line_direct(
            lat1_rad, lon1_rad, bearing_rad, distance, WGS84_A, WGS84_E2
        )
    
    # Convert back to degrees
    new_latitude = math.degrees(new_lat_rad)
    new_longitude = math.degrees(new_lon_rad)
    
    # Normalize longitude to [-180, 180]
    new_longitude = ((new_longitude + 180) % 360) - 180
    
    # For this implementation, we'll keep elevation constant
    # In a more sophisticated implementation, you might adjust for terrain
    new_elevation = elevation
    
    return (new_latitude, new_longitude, new_elevation)


def _vincenty_direct(lat1, lon1, bearing, distance, a, f):
    """
    Vincenty's direct formula for great circle calculations on an ellipsoid.
    
    Parameters:
    -----------
    lat1, lon1 : float
        Starting coordinates in radians
    bearing : float
        Bearing in radians
    distance : float
        Distance in meters
    a : float
        Semi-major axis of ellipsoid
    f : float
        Flattening of ellipsoid
    
    Returns:
    --------
    tuple
        (lat2, lon2) in radians
    """
    
    b = a * (1 - f)
    sin_alpha1 = math.sin(bearing)
    cos_alpha1 = math.cos(bearing)
    
    tan_u1 = (1 - f) * math.tan(lat1)
    cos_u1 = 1 / math.sqrt(1 + tan_u1**2)
    sin_u1 = tan_u1 * cos_u1
    
    sigma1 = math.atan2(tan_u1, cos_alpha1)
    sin_alpha = cos_u1 * sin_alpha1
    
    cos2_alpha = 1 - sin_alpha**2
    u2 = cos2_alpha * (a**2 - b**2) / (b**2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    
    sigma = distance / (b * A)
    sigma_prev = 2 * math.pi
    
    # Iterate until convergence
    while abs(sigma - sigma_prev) > 1e-12:
        cos_2sigma_m = math.cos(2 * sigma1 + sigma)
        sin_sigma = math.sin(sigma)
        cos_sigma = math.cos(sigma)
        
        delta_sigma = B * sin_sigma * (
            cos_2sigma_m + B / 4 * (
                cos_sigma * (-1 + 2 * cos_2sigma_m**2) -
                B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma**2) * (-3 + 4 * cos_2sigma_m**2)
            )
        )
        
        sigma_prev = sigma
        sigma = distance / (b * A) + delta_sigma
    
    tmp = sin_u1 * sin_sigma - cos_u1 * cos_sigma * cos_alpha1
    lat2 = math.atan2(
        sin_u1 * cos_sigma + cos_u1 * sin_sigma * cos_alpha1,
        (1 - f) * math.sqrt(sin_alpha**2 + tmp**2)
    )
    
    lambda_val = math.atan2(
        sin_sigma * sin_alpha1,
        cos_u1 * cos_sigma - sin_u1 * sin_sigma * cos_alpha1
    )
    
    C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
    L = lambda_val - (1 - C) * f * sin_alpha * (
        sigma + C * sin_sigma * (
            cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m**2)
        )
    )
    
    lon2 = (lon1 + L + 3 * math.pi) % (2 * math.pi) - math.pi
    
    return lat2, lon2


def _rhumb_line_direct(lat1, lon1, bearing, distance, a, e2):
    """
    Rhumb line (constant bearing) calculation on an ellipsoid.
    
    Parameters:
    -----------
    lat1, lon1 : float
        Starting coordinates in radians
    bearing : float
        Bearing in radians
    distance : float
        Distance in meters
    a : float
        Semi-major axis of ellipsoid
    e2 : float
        First eccentricity squared
    
    Returns:
    --------
    tuple
        (lat2, lon2) in radians
    """
    
    # Handle special cases where bearing is due north or south
    if abs(math.sin(bearing)) < 1e-10:
        # Pure north or south movement
        M1 = _meridional_radius_of_curvature(lat1, a, e2)
        delta_lat = distance * math.cos(bearing) / M1
        lat2 = lat1 + delta_lat
        lat2 = max(-math.pi/2, min(math.pi/2, lat2))
        return lat2, lon1
    
    # Handle special cases where bearing is due east or west
    if abs(math.cos(bearing)) < 1e-10:
        # Pure east or west movement
        N1 = _prime_vertical_radius_of_curvature(lat1, a, e2)
        delta_lon = distance * math.sin(bearing) / (N1 * math.cos(lat1))
        lon2 = lon1 + delta_lon
        return lat1, lon2
    
    # General rhumb line calculation
    # Calculate change in latitude
    M1 = _meridional_radius_of_curvature(lat1, a, e2)
    delta_lat = distance * math.cos(bearing) / M1
    lat2 = lat1 + delta_lat
    
    # Ensure latitude is within valid range
    lat2 = max(-math.pi/2, min(math.pi/2, lat2))
    
    # Use isometric latitude for rhumb line calculations
    def isometric_latitude(lat):
        e = math.sqrt(e2)
        if abs(lat) >= math.pi/2:
            # Handle poles
            return math.copysign(float('inf'), lat)
        
        sin_lat = math.sin(lat)
        return math.log(math.tan(math.pi/4 + lat/2)) - e/2 * math.log(
            (1 + e * sin_lat) / (1 - e * sin_lat)
        )
    
    iso_lat1 = isometric_latitude(lat1)
    iso_lat2 = isometric_latitude(lat2)
    delta_iso_lat = iso_lat2 - iso_lat1
    
    # Calculate change in longitude
    if abs(delta_iso_lat) < 1e-10:
        # Parallel of latitude case (very small latitude change)
        N1 = _prime_vertical_radius_of_curvature(lat1, a, e2)
        delta_lon = distance * math.sin(bearing) / (N1 * math.cos(lat1))
    else:
        # Standard rhumb line calculation
        delta_lon = delta_iso_lat * math.tan(bearing)
    
    lon2 = lon1 + delta_lon
    
    return lat2, lon2


def _meridional_radius_of_curvature(lat, a, e2):
    """
    Calculate the meridional radius of curvature at a given latitude.
    
    Parameters:
    -----------
    lat : float
        Latitude in radians
    a : float
        Semi-major axis of ellipsoid
    e2 : float
        First eccentricity squared
    
    Returns:
    --------
    float
        Meridional radius of curvature in meters
    """
    sin_lat = math.sin(lat)
    return a * (1 - e2) / (1 - e2 * sin_lat**2)**1.5


def _prime_vertical_radius_of_curvature(lat, a, e2):
    """
    Calculate the prime vertical radius of curvature at a given latitude.
    
    Parameters:
    -----------
    lat : float
        Latitude in radians
    a : float
        Semi-major axis of ellipsoid
    e2 : float
        First eccentricity squared
    
    Returns:
    --------
    float
        Prime vertical radius of curvature in meters
    """
    sin_lat = math.sin(lat)
    return a / math.sqrt(1 - e2 * sin_lat**2)
