#!/usr/bin/env python3
"""
TT80Calculator: A standalone Python script for calculating 15 equidistant 
geographic points with linear elevation interpolation between two given coordinates.

Author: Generated Script
Date: July 10, 2025
Requirements: Python 3.x with standard library only
"""

import math
import sys
import pandas as pd


def validate_coordinates(lat, lon, elevation, point_name="Point"):
    """
    Validate latitude, longitude, and elevation values.
    
    Args:
        lat (float): Latitude in decimal degrees
        lon (float): Longitude in decimal degrees  
        elevation (float): Elevation in meters
        point_name (str): Name of the point for error messages
        
    Returns:
        bool: True if valid, raises ValueError if invalid
    """
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) or not isinstance(elevation, (int, float)):
        raise ValueError(f"{point_name}: Coordinates and elevation must be numeric values")
    
    if lat < -90 or lat > 90:
        raise ValueError(f"{point_name}: Latitude must be between -90 and 90 degrees. Got: {lat}")
    
    if lon < -180 or lon > 180:
        raise ValueError(f"{point_name}: Longitude must be between -180 and 180 degrees. Got: {lon}")
    
    if elevation < -11000 or elevation > 9000:  # Reasonable Earth elevation bounds
        raise ValueError(f"{point_name}: Elevation seems unrealistic. Got: {elevation} meters")
    
    return True


def degrees_to_radians(degrees):
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0


def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * 180.0 / math.pi

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
    azimuth = round(azimuth, 5)
    dist = round(dist, 2)
    
    # print(azimuth, dist)
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

####
def calculate_great_circle_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth using Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of first point in decimal degrees
        lat2, lon2: Latitude and longitude of second point in decimal degrees
        
    Returns:
        float: Distance in meters
    """
    # Earth's radius in meters
    R = 6378137.0
    
    # Convert to radians
    lat1_rad = degrees_to_radians(lat1)
    lon1_rad = degrees_to_radians(lon1)
    lat2_rad = degrees_to_radians(lat2)
    lon2_rad = degrees_to_radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat / 2) ** 2 + 
          math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def calculate_initial_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the initial bearing from point 1 to point 2.
    
    Args:
        lat1, lon1: Latitude and longitude of first point in decimal degrees
        lat2, lon2: Latitude and longitude of second point in decimal degrees
        
    Returns:
        float: Initial bearing in radians
    """
    lat1_rad = degrees_to_radians(lat1)
    lat2_rad = degrees_to_radians(lat2)
    dlon_rad = degrees_to_radians(lon2 - lon1)
    
    y = math.sin(dlon_rad) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
          math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
    
    bearing = math.atan2(y, x)
    return bearing
####

def calculate_destination_point(lat, lon, bearing, distance):
    """
    Calculate destination point given start point, bearing, and distance.
    
    Args:
        lat, lon: Starting latitude and longitude in decimal degrees
        bearing: Bearing in radians
        distance: Distance in meters
        
    Returns:
        tuple: (latitude, longitude) in decimal degrees
    """
    # Earth's radius in meters
    R = 6378137.0
    
    lat_rad = degrees_to_radians(lat)
    lon_rad = degrees_to_radians(lon)
    
    # Angular distance
    angular_distance = distance / R
    
    # Calculate destination latitude
    lat2_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance) +
        math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing)
    )
    
    # Calculate destination longitude
    lon2_rad = lon_rad + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(lat2_rad)
    )
    
    # Convert back to degrees
    lat2 = radians_to_degrees(lat2_rad)
    lon2 = radians_to_degrees(lon2_rad)
    
    # Normalize longitude to [-180, 180]
    lon2 = ((lon2 + 180) % 360) - 180
    
    return lat2, lon2


def calculate_elevation_slope(elevation1, elevation2, total_distance):
    """
    Calculate the linear slope between two elevation points.
    
    Args:
        elevation1 (float): Starting elevation in meters
        elevation2 (float): Ending elevation in meters
        total_distance (float): Total horizontal distance in meters
        
    Returns:
        float: Slope in meters per meter (rise/run)
    """
    if total_distance == 0:
        return 0.0
    
    # elevation_change = elevation2 - elevation1
    # slope = elevation_change / total_distance
    
    elevation_change = elevation2 - elevation1
    slope_ratio = elevation_change / total_distance
    slope = math.atan(slope_ratio) #Radians


    return slope


def interpolate_elevation(start_elevation, slope, distance_along_path):
    """
    Calculate elevation at a given distance along the path using linear interpolation.
    
    Args:
        start_elevation (float): Starting elevation in meters
        slope (float): Slope in meters per meter
        distance_along_path (float): Distance from start point in meters
        
    Returns:
        float: Interpolated elevation in meters
    """
    elevation = start_elevation + (slope * distance_along_path)
    return elevation


def generate_equidistant_points(lat1, lon1, elev1, lat2, lon2, elev2, num_points=15):
    """
    Generate equidistant points between two geographic coordinates with elevation interpolation.
    
    Args:
        lat1, lon1, elev1: Starting point coordinates and elevation
        lat2, lon2, elev2: Ending point coordinates and elevation
        num_points (int): Number of intermediate points to generate
        
    Returns:
        tuple: (points_list, pandas_dataframe, total_distance, elevation_slope)
    """
    # Validate input coordinates
    validate_coordinates(lat1, lon1, elev1, "Start point")
    validate_coordinates(lat2, lon2, elev2, "End point")
    
    
    ##### Calculate total distance and bearing
    # total_distance = calculate_great_circle_distance(lat1, lon1, lat2, lon2)
    initial_bearing = calculate_initial_bearing(lat1, lon1, lat2, lon2)
    #####
    
    
    #####
    pt1 = (lat1, lon1)
    pt2 = (lat2, lon2)
    _ , total_distance = distance(pt1, pt2, ellipsoid='WGS84', method='great_circle', back_az=False)
    #####
    
    
    
    
    #################
    
    # Calculate elevation slope
    #####
    # initial_bearing = math.radians(initial_bearing) #Since swapping in simple_distance math, need radians not deg for proper TT80 alignment   
    #####
    
    elevation_slope = calculate_elevation_slope(elev1, elev2, total_distance)
    
    # Generate points
    points = []
    
    # Distance interval between points
    distance_interval = total_distance / (num_points + 1)
    
    # Add start point to the data
    start_point = {
        'point_number': 0,
        # 'point_type': 'Start',
        'point_type': 'Rwy_Start',
        'latitude': lat1,
        'longitude': lon1,
        'elevation_m': elev1,
        'distance_from_start_m': 0.0
    }
    points.append(start_point)
    
    # Generate intermediate points
    for i in range(1, num_points + 1):
        # Calculate distance from start point
        distance_from_start = distance_interval * i
        
        # Calculate coordinates
        lat, lon = calculate_destination_point(lat1, lon1, initial_bearing, distance_from_start)
        
        # Calculate elevation
        elevation = interpolate_elevation(elev1, elevation_slope, distance_from_start)
        
        # Store point
        point = {
            'point_number': i,
            # 'point_type': 'Intermediate',
            'point_type': f'TT80_pt_{i}',
            'latitude': lat,
            'longitude': lon,
            'elevation_m': elevation,
            'distance_from_start_m': distance_from_start
        }
        points.append(point)
    
    # Add end point to the data
    end_point = {
        'point_number': num_points + 1,
        # 'point_type': 'End',
        'point_type': 'Rwy_End',
        'latitude': lat2,
        'longitude': lon2,
        'elevation_m': elev2,
        'distance_from_start_m': total_distance
    }
    points.append(end_point)
    
    # Create pandas DataFrame
    df = pd.DataFrame(points)
    
    # Add calculated columns
    # df['distance_km'] = df['distance_from_start'] / 1000.0
    # df['elevation_gain_from_start'] = df['elevation'] - elev1
    
    # Round numeric values for cleaner display
    df['latitude'] = df['latitude'].round(9)
    df['longitude'] = df['longitude'].round(9)
    df['elevation_m'] = df['elevation_m'].round(5)
    df['distance_from_start_m'] = df['distance_from_start_m'].round(5)
    # df['distance_km'] = df['distance_km'].round(5)
    # df['elevation_gain_from_start'] = df['elevation_gain_from_start'].round(5)
    
    # Extract only intermediate points for backward compatibility
    intermediate_points = [p for p in points if p['point_type'] == 'Intermediate']
    
    return intermediate_points, df, total_distance, elevation_slope


def format_output(start_point, end_point, points, df, total_distance, elevation_slope):
    """
    Format and display the results in a clear, readable format.
    
    Args:
        start_point (tuple): (lat, lon, elevation) of start point
        end_point (tuple): (lat, lon, elevation) of end point
        points (list): List of intermediate points
        df (pandas.DataFrame): DataFrame containing all points
        total_distance (float): Total distance in meters
        elevation_slope (float): Elevation slope
    """
    lat1, lon1, elev1 = start_point
    lat2, lon2, elev2 = end_point
    
    print("=" * 80)
    print("TT80 CALCULATOR RESULTS")
    print("=" * 80)
    print()
    print("INPUT COORDINATES:")
    print(f"Start Point: Lat {lat1:11.6f}°, Lon {lon1:11.6f}°, Elevation {elev1:8.2f} m")
    print(f"End Point:   Lat {lat2:11.6f}°, Lon {lon2:11.6f}°, Elevation {elev2:8.2f} m")
    print()
    print("CALCULATIONS:")
    print(f"Total Distance:    {total_distance:12.2f} meters ({total_distance/1000:.3f} km)")
    print(f"Elevation Change:  {elev2-elev1:12.2f} meters")
    print(f"Elevation Slope:   {elevation_slope:12.6f} m/m ({elevation_slope*100:.4f}%)")
    print()
    print("15 EQUIDISTANT INTERMEDIATE POINTS:")
    print("-" * 80)
    print("Point#    Latitude     Longitude    Elevation   Distance from Start")
    print("-" * 80)
    
    for point in points:
        print(f"{point['point_number']:6d}   "
              f"{point['latitude']:11.6f}°  "
              f"{point['longitude']:11.6f}°  "
              f"{point['elevation']:9.2f} m  "
              f"{point['distance_from_start']:10.2f} m")
    
    print("-" * 80)
    print(f"Total points generated: {len(points)}")
    print("=" * 80)
    print()
    print("PANDAS DATAFRAME SUMMARY:")
    print("-" * 50)
    print(f"DataFrame shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print("Columns:", list(df.columns))
    print()
    print("First 5 rows of DataFrame:")
    print(df.head().to_string(index=False))
    print()
    print("Last 5 rows of DataFrame:")
    print(df.tail().to_string(index=False))


def display_dataframe_info(df):
    """
    Display comprehensive information about the DataFrame.
    
    Args:
        df (pandas.DataFrame): The DataFrame to analyze
    """
    print("\n" + "=" * 60)
    print("DATAFRAME ANALYSIS")
    print("=" * 60)
    
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"Memory usage: {df.memory_usage(deep=True).sum()} bytes")
    print()
    
    print("Column Information:")
    print("-" * 30)
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        print(f"{col:25}: {dtype:10} ({null_count} nulls)")
    
    print()
    print("Statistical Summary (Numeric Columns):")
    print("-" * 40)
    print(df.describe().round(3))
    
    print()
    print("Complete DataFrame:")
    print("-" * 20)
    print(df.to_string(index=False))


def save_dataframe(df, filename=None, format_type='csv'):
    """
    Save DataFrame to various formats.
    
    Args:
        df (pandas.DataFrame): DataFrame to save
        filename (str): Optional filename (without extension)
        format_type (str): Format type ('csv', 'excel', 'json')
    
    Returns:
        str: Filename of saved file
    """
    if filename is None:
        filename = "tt80_waypoints"
    
    if format_type.lower() == 'csv':
        full_filename = f"{filename}.csv"
        df.to_csv(full_filename, index=False)
    elif format_type.lower() == 'excel':
        full_filename = f"{filename}.xlsx"
        df.to_excel(full_filename, index=False)
    elif format_type.lower() == 'json':
        full_filename = f"{filename}.json"
        df.to_json(full_filename, orient='records', indent=2)
    else:
        raise ValueError("Unsupported format. Use 'csv', 'excel', or 'json'")
    
    return full_filename


# def get_user_input():
#     """
#     Get coordinate inputs from the user via command line.
    
#     Returns:
#         tuple: ((lat1, lon1, elev1), (lat2, lon2, elev2))
#     """
#     print("TT80 Calculator - Geographic Point Generator")
#     print("=" * 50)
#     print("Enter coordinates in decimal degrees and elevation in meters")
#     print()
    
#     try:
#         # Get start point
#         print("START POINT:")
#         lat1 = float(input("Enter start latitude (decimal degrees): "))
#         lon1 = float(input("Enter start longitude (decimal degrees): "))
#         elev1 = float(input("Enter start elevation (meters): "))
#         print()
        
#         # Get end point
#         print("END POINT:")
#         lat2 = float(input("Enter end latitude (decimal degrees): "))
#         lon2 = float(input("Enter end longitude (decimal degrees): "))
#         elev2 = float(input("Enter end elevation (meters): "))
#         print()
        
#         return (lat1, lon1, elev1), (lat2, lon2, elev2)
        
#     except ValueError as e:
#         raise ValueError("Invalid input: Please enter numeric values only")


# def main():
#     """
#     Main function to run the TT80 Calculator.
#     """
#     try:
#         # Get user input
#         start_point = 36.07365833, -115.125825,	698.09472
#         end_point = 36.07362778,-115.1614333, 735.07152
#         lat1, lon1, elev1 = start_point
#         lat2, lon2, elev2 = end_point
#         # 36.07365833	-115.125825	698.09472

#         # 36.07362778	-115.1614333 735.07152



#         # Generate equidistant points
#         points, df, total_distance, elevation_slope = generate_equidistant_points(
#             lat1, lon1, elev1, lat2, lon2, elev2
#         )
        
#         # Display results
#         format_output(start_point, end_point, points, df, total_distance, elevation_slope)
        
#         # Display detailed DataFrame information
#         detail_option = input("\nWould you like to see detailed DataFrame analysis? (y/n): ").lower().strip()
#         if detail_option in ['y', 'yes']:
#             display_dataframe_info(df)
        
#         # Optionally save DataFrame to file
#         save_option = input("\nWould you like to save the data to a file? (y/n): ").lower().strip()
#         if save_option in ['y', 'yes']:
#             format_choice = input("Choose format (csv/json): ").lower().strip()
#             if format_choice not in ['csv', 'json']:
#                 format_choice = 'csv'
            
#             filename = input("Enter filename (without extension): ").strip()
#             if not filename:
#                 filename = "tt80_waypoints"
            
#             saved_filename = save_dataframe(df, filename, format_choice)
#             print(f"Data saved to {saved_filename}")
#             print(f"DataFrame contains {df.shape[0]} rows and {df.shape[1]} columns")
        
#     except ValueError as e:
#         print(f"Error: {e}")
#         sys.exit(1)
#     except KeyboardInterrupt:
#         print("\nOperation cancelled by user.")
#         sys.exit(0)
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         sys.exit(1)


# def run_example():
#     """
#     Run an example calculation for demonstration purposes.
#     """
#     print("Running example calculation...")

    
#     # Example coordinates (Mount Whitney to Death Valley)
#     lat1, lon1, elev1 = 36.07640268, -115.1258227, 696.4248
#   # Mount Whitney summit
#     lat2, lon2, elev2 = 36.07636667, -115.1701917, 742.67136
#    # Death Valley
    
#     points, df, total_distance, elevation_slope = generate_equidistant_points(
#         lat1, lon1, elev1, lat2, lon2, elev2
#     )
    
#     format_output((lat1, lon1, elev1), (lat2, lon2, elev2), points, df, total_distance, elevation_slope)
    
#     # Save example data to CSV for demonstration
#     print("\nSaving example data to 'tt80_example.csv'...")
#     df.to_csv('tt80_example.csv', index=False)
#     print("Example data saved successfully!")


# if __name__ == "__main__":
#     if len(sys.argv) > 1 and sys.argv[1].lower() == "example":
#         run_example()
#     else:
        # main()
