# -*- coding: utf-8 -*-
"""
Created on Thu Aug  7 14:03:25 2025

@author: dukes
"""
#Environment imports
import math
from math import radians, degrees
import pandas as pd
import uuid
from magvar import magnetic_variation

#Custom imports
from TT80Calculator import calculate_destination_point
from TT80Calculator import generate_equidistant_points
from TT80Calculator import distance
from coordinate_generator import generate_wgs84_coordinate
from create_icao_kml import icao_kml
from geoidheight_fortran import geoidheight




#Simple conversion methods
def f2m(feet):
    return feet * 0.3048

def m2f(meters):
    return meters * 3.28084

def nm2f(nautical_miles):
    return nautical_miles * 6076.12

#KML Runway Generator for Google Earth Demonstration
def makerunway_kml(df2proc, icao, TD_dist_ft, STP_dist_ft, G_Slope, TP_Alt, RWY_W, GA_Spd, Dep_dist_nm):  
    
    print("Processing (.kml)")
    UUID = (uuid.uuid4().hex).upper()    #32 bit hash required for OMNI
    
    kml_output_PRE = ''
    kml_output_RWY = ''
    kml_output_POST = ''
    
    TP_Alt_base = TP_Alt #to avoid mutation in loop
    
    for _, row in df2proc.iterrows():
        setup_kwargs = {}
        manual_kwargs = {}
        df_kwargs     = {}
        
        #HI
        manual_kwargs['uuid'] = UUID
        manual_kwargs['icao'] = icao
        manual_kwargs['rwy_w'] = RWY_W
        
        manual_kwargs['hi_ident'] = str(row['hi_ident'])
        
        hi_wgs_lat = float(row['hi_wgs_lat'])
        manual_kwargs['hi_wgs_lat'] = hi_wgs_lat
        
        hi_wgs_long = float(row['hi_wgs_long'])
        manual_kwargs['hi_wgs_long'] = hi_wgs_long
        
        hi_elev_ft = float(row['hi_elev'])
        manual_kwargs['hi_elev_ft'] = hi_elev_ft
        
        hi_disp_thld_ft= float(row['hi_disp_thld']) 
        manual_kwargs['hi_disp_thld_ft'] = hi_disp_thld_ft
              
        
        # #LO
        manual_kwargs['lo_ident'] = str(row['lo_ident'])
        
        
        
        
        lo_wgs_lat = float(row['lo_wgs_lat'])
        manual_kwargs['lo_wgs_lat'] = lo_wgs_lat    
        
        lo_wgs_long = float(row['lo_wgs_long'])
        manual_kwargs['lo_wgs_long'] = lo_wgs_long
        
        
        
        
        
        #MUST BE FIXED TO ACCOUNT FOR SHORTENED RUNWAY END
        lo_elev_ft = float(row['lo_elev'])
        manual_kwargs['lo_elev_ft'] = float(row['lo_elev'])

        
        lo_disp_thld_ft= float(row['lo_disp_thld'])
        manual_kwargs['lo_disp_thld_ft']  = lo_disp_thld_ft
        
        
        #Approach and departure variables from GUI input
        setup_kwargs['G_Slope'] = float(G_Slope)
        setup_kwargs['TD_dist_ft'] = float(TD_dist_ft)
        setup_kwargs['STP_dist_ft'] = float(STP_dist_ft)

        TP_Alt = TP_Alt_base
        if hi_elev_ft > lo_elev_ft:
            TP_Alt = math.ceil((hi_elev_ft + float(TP_Alt))/100)*100
        elif lo_elev_ft > hi_elev_ft:
            TP_Alt = math.ceil((lo_elev_ft + float(TP_Alt))/100)*100
        manual_kwargs['TP_Alt'] = float(TP_Alt)
        
        setup_kwargs['Go_Around_Spd'] = GA_Spd    
        setup_kwargs['Dep_dist_nm'] = Dep_dist_nm
        
        
        #Additional inputs from defaults pop-up
        setup_kwargs['App_Point_Offset'] = 0.0                                                  
        setup_kwargs['Min_App_Angle'] = float(G_Slope) - 0.5                                           
        setup_kwargs['Alt_Valid_Distance'] = 3000                                               
        setup_kwargs['Min_Departure_Angle'] = 2                                                 
        setup_kwargs['min_clnc_slope'] = float(2.5)
        
        setup_kwargs['Go_Around_Alt'] = TP_Alt                                                  
        setup_kwargs['Release_Alt'] = TP_Alt                                                                                                      
        setup_kwargs['Acceleration_Alt'] = TP_Alt   
        
        #Runway bearing in degrees and radians, also runway bearing in true and ~magnetic based on magvar function ()
        rw_brg_deg,_ = distance((hi_wgs_lat, hi_wgs_long), (lo_wgs_lat, lo_wgs_long)) #returns Tuple of (azimuth_degrees (normalized 360), distance_meters)    
        rev_rw_brg_deg = (rw_brg_deg - 180) % 360
        manual_kwargs['rw_brg_deg'] = rw_brg_deg
        manual_kwargs['rev_rw_brg_deg'] = rev_rw_brg_deg
        
        # declination_rad = magnetic_variation(2022.05, radians(hi_wgs_lat), radians(hi_wgs_long), hi_elev_ft) 
        # mag_var = degrees(declination_rad)
        
        mag_var= row['var']
        manual_kwargs['mag_var'] = mag_var

        manual_kwargs['rwy_hdg_tru'] = rw_brg_deg % 360
        manual_kwargs['rwy_hdg_mag'] = (rw_brg_deg - mag_var) % 360

        rw_brg_rad = math.radians(rw_brg_deg) % (2 * math.pi)
        rev_rw_brg_rad = rw_brg_rad-math.pi % (2 * math.pi)
        manual_kwargs['rw_brg_rad'] = rw_brg_rad
        manual_kwargs['rev_rw_brg_rad'] = rev_rw_brg_rad
        
        
        #MOD RUNWAY END Coordinates
        if row['hi_redux'] != 0:     
			
            mod_endpts = generate_wgs84_coordinate(row['lo_wgs_lat'], row['lo_wgs_long'], lo_elev_ft, rev_rw_brg_deg, f2m(float(row['hi_redux'])), 
			method='great_circle')
        
            lo_wgs_lat = mod_endpts[0] 
            manual_kwargs['lo_wgs_lat'] = mod_endpts[0]    
            
            lo_wgs_long = mod_endpts[1] 
            manual_kwargs['lo_wgs_long'] = mod_endpts[1] 
        
        
        
        #distance method returns Tuple of (azimuth_degrees, distance_meters) we dont need the az here since already computing 
        values = distance((hi_wgs_lat, hi_wgs_long), (lo_wgs_lat, lo_wgs_long), ellipsoid='WGS84', method='great_circle', back_az=False)  #az and back_as in deg NOT RAD
        rw_dist_m = values[1]
        manual_kwargs['rw_dist_ft'] = m2f(rw_dist_m)
        
        #STP_Point Coordinates
        manual_kwargs['STP_points'] = generate_wgs84_coordinate(lo_wgs_lat, lo_wgs_long, lo_elev_ft, rev_rw_brg_deg, f2m(float(STP_dist_ft)), 
                                    method='great_circle')
        
        #DEPT_Point Coordinates
        distance_ft = nm2f(float(Dep_dist_nm))
        dep_climb_angle_rad = math.atan(float(TP_Alt_base) / distance_ft)
        dep_climb_angle_deg = math.degrees(dep_climb_angle_rad) #double tap so we can display calc climb angle
        manual_kwargs['dep_climb_angle_deg'] = dep_climb_angle_deg

        dep_horizontal_distance_ft = float(TP_Alt_base) / math.tan(dep_climb_angle_rad)
        manual_kwargs['DEP_points'] = generate_wgs84_coordinate(lo_wgs_lat, lo_wgs_long, lo_elev_ft, rw_brg_deg, f2m(float(dep_horizontal_distance_ft)), 
                                    method='great_circle')
        
        if pd.isna(row['hi_disp_thld']): #if no displaced threshold
            stpt_lat, stpt_long = hi_wgs_lat, hi_wgs_long
            manual_kwargs['stpt_lat'], manual_kwargs['stpt_long'] = stpt_lat, stpt_long 
            
            hi_disp_thld_lat, hi_disp_thld_long = hi_wgs_lat, hi_wgs_long
            manual_kwargs['hi_disp_thld_lat'], manual_kwargs['hi_disp_thld_long'] = hi_disp_thld_lat, hi_disp_thld_long
            manual_kwargs['hi_disp_thld_ft'] = 0
            
            #TD_Point Coordinates
            manual_kwargs['TD_points'] = generate_wgs84_coordinate(stpt_lat, stpt_long, hi_elev_ft, rw_brg_deg, f2m(float(TD_dist_ft)), 
                                        method='great_circle')
            
            #APP_Point Coordinates
            climb_angle_rad = math.radians(float(G_Slope))
            horizontal_distance_ft = float(TP_Alt_base) / math.tan(climb_angle_rad)
            manual_kwargs['APP_points'] = generate_wgs84_coordinate(stpt_lat, stpt_long, hi_elev_ft, rev_rw_brg_deg, f2m(float(horizontal_distance_ft)), 
                                        method='great_circle')
            
            #TT80 POINTS
            stpt_a = hi_elev_ft
            intermediate_points, tt80df, total_distance, rwy_slope_rad = generate_equidistant_points(stpt_lat, stpt_long, stpt_a*0.3408, 
                                                                            lo_wgs_lat, lo_wgs_long, row['lo_elev']*0.3408, 
                                                                            num_points=15)
            
            rwy_slope_deg = math.degrees(rwy_slope_rad)
            print(f'RWY {manual_kwargs['hi_ident']} - Total Distance: {m2f(total_distance):.0f} / Slope: {rwy_slope_deg:.1f}° / Runway Heading: {round((rw_brg_deg - mag_var),1)}°')
       
            manual_kwargs['total_distance_m'] = total_distance
            manual_kwargs['total_distance_ft'] = m2f(total_distance)
            manual_kwargs['rwy_slope_deg'] = rwy_slope_deg
            
            for tt80index, tt80row in tt80df.iterrows():
                tt80df.at[tt80index, 'emg96ft'] = math.ceil(m2f(geoidheight(tt80row['latitude'], tt80row['longitude'])))
                tt80df.at[tt80index, 'distance_from_start_ft'] = round(m2f(tt80row['distance_from_start_m']),0)
            for tt80index, tt80row in tt80df.iterrows():
                tt80df.at[tt80index, 'ptEGM96akt'] = m2f(tt80row['elevation_m']) - tt80row['emg96ft']
            
            manual_kwargs['GSV_alt'] = tt80df.iloc[6]['emg96ft']
            
            df_kwargs = {"intermediate_points": tt80df}
            
            ###MAKE DYNAMIC SAVE
            tt80df.to_csv(fr"C:\Users\dukes\Sync\AriesCI\ATOLv4_2025\FINAL\RETURNS\{icao}\TT80_{row['hi_ident']}.csv", index=False)
                  
        elif not pd.isna(row['hi_disp_thld']): #if displaced threshold
            stpt_lat, stpt_long = calculate_destination_point(hi_wgs_lat, hi_wgs_long, rw_brg_rad, f2m(row['hi_disp_thld']))  #start lat lon, brg(rad) dist(m)
            manual_kwargs['stpt_lat'], manual_kwargs['stpt_long'] = stpt_lat, stpt_long 
            
            hi_disp_thld_lat, hi_disp_thld_long = hi_wgs_lat, hi_wgs_long
            manual_kwargs['hi_disp_thld_lat'], manual_kwargs['hi_disp_thld_long'] = hi_disp_thld_lat, hi_disp_thld_long
            manual_kwargs['hi_disp_thld_ft'] = float(row['hi_disp_thld'])
            #TD_Point Coordinates
            manual_kwargs['TD_points'] = generate_wgs84_coordinate(stpt_lat, stpt_long, hi_elev_ft, rw_brg_deg, f2m(float(TD_dist_ft)), 
                                        method='great_circle')
            
            #APP_Point Coordinates
            climb_angle_rad = math.radians(float(G_Slope))
            horizontal_distance_ft = float(TP_Alt_base) / math.tan(climb_angle_rad)
            manual_kwargs['APP_points'] = generate_wgs84_coordinate(stpt_lat, stpt_long, hi_elev_ft, rev_rw_brg_deg, f2m(float(horizontal_distance_ft)), 
                                        method='great_circle')

            #TT80 POINTS
            stpt_a = row['hi_disp_thld_elev']
            intermediate_points, tt80df, total_distance, rwy_slope_rad = generate_equidistant_points(stpt_lat, stpt_long, stpt_a*0.3408, 
                                                                            lo_wgs_lat, lo_wgs_long, row['lo_elev']*0.3408, num_points=15)
            
            rwy_slope_deg = math.degrees(rwy_slope_rad)
            print(f'RWY {manual_kwargs['hi_ident']} - Total Distance: {m2f(total_distance):.0f} / Slope: {rwy_slope_deg:.1f}° / Runway Heading: {round((rw_brg_deg - mag_var),3)}°')
                  
            manual_kwargs['total_distance_m'] = total_distance
            manual_kwargs['total_distance_ft'] = m2f(total_distance)
            manual_kwargs['rwy_slope_deg'] = rwy_slope_deg                                               
            
            for tt80index, tt80row in tt80df.iterrows():
                tt80df.at[tt80index, 'emg96ft'] = math.ceil(m2f(geoidheight(tt80row['latitude'], tt80row['longitude'])))
                tt80df.at[tt80index, 'distance_from_start_ft'] = round(m2f(tt80row['distance_from_start_m']),0)
                
            for tt80index, tt80row in tt80df.iterrows():
                tt80df.at[tt80index, 'ptEGM96alt'] = m2f(tt80row['elevation_m']) - tt80row['emg96ft']
            
            manual_kwargs['GSV_alt'] = tt80df.iloc[6]['emg96ft']
            
            df_kwargs = {"intermediate_points": tt80df}   
            tt80df.to_csv(fr'C:\Users\dukes\Sync\AriesCI\ATOLv4_2025\FINAL\RETURNS\{icao}\TT80_{row['hi_ident']}.csv', index=False)
    
        manual_kwargs['runway_remaining'] = manual_kwargs['total_distance_ft'] - setup_kwargs['TD_dist_ft'] - setup_kwargs['STP_dist_ft']
        
        
        all_kargs = {**manual_kwargs, **setup_kwargs, **df_kwargs}
        
        #LOG
        with pd.option_context('display.max_columns', None):

            with open(fr'C:\Users\dukes\Sync\AriesCI\ATOLv4_2025\FINAL\RETURNS\{icao}\{icao}_log.txt', "a") as logfile:
                for key, value in all_kargs.items():
                    logfile.write(f"{key}: {value}\n")


        kml_output_RWY += icao_kml(runways=all_kargs, icao=None, finalize=False)
        
    kml_output_PRE = icao_kml(runways=None, icao=icao, setup=True)
    kml_output_POST += icao_kml(runways=None, icao=icao, finalize=True)
    
    kml_path = f"C:/Users/dukes/Sync/AriesCI/ATOLv4_2025/FINAL/RETURNS/{icao}/{icao}_runways.kml"
    
    with open(kml_path, "w", encoding="utf-8") as kml_file:
        kml_file.write(kml_output_PRE + kml_output_RWY + kml_output_POST)
        
        
    # def configure_runway(**kwargs):
    #     print("Runway Configuration:")
    #     for key, value in kwargs.items():
    #         print(f"{key}: {value}")
    
    # Manual definitions
    # manual_kwargs = {
    #     "heading": 90.0,
    #     "length": 3000,
    #     "surface_type": "asphalt"
    # }
    
    # # Loop-generated arguments for tt80points
    # loop_args = {}
    # for i in range(1, 6):
    #     loop_args[f"marker_{i}"] = f"Point-{i}"
    
    # # Combine both
    # all_args = {**manual_kwargs, **loop_args}
    
    # # Pass to function
    # # configure_runway(**all_args)
    
    # create_icao_kml(**all_args)
    # create_icao_xml(**all_args)



