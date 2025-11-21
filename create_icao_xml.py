# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 09:53:40 2025

@author: dukes
"""
import math

def icao_xml(UUID, runways=None, icao=None, setup=False, finalize=False):
    
    xml_output = ''
    
    if setup:

        xml_output += '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_output += '#################################################################\n'
        xml_output += '#########                   ADD xmlns                   #########\n'
        xml_output += '#################################################################\n'
        # xml_output += '<TerminalProcedure xmlns:common="http://aero.lmco.com/adp/e3/common_types" xmlns:uci="http://uas-c2-initiative.mil/" xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xmlns:AAA="urn:us:gov:actdf" xmlns:AD="urn:us:gov:basic" xmlns:AB="urn:us:gov:ism" xmlns:AC="urn:us:gov:ism-cvenum" xmlns:tasking="urn:us:gov:tasking">\n'			
        xml_output += '\t<RunwaySurveyTimeStamp>2011-05-02T18:30:30Z</RunwaySurveyTimeStamp>\n'
        xml_output += '\t<RunwaySurveyVersion>361</RunwaySurveyVersion>\n'
        xml_output += f"\t<Id>{UUID}</Id>\n"
        xml_output += '\t<State>Save</State>\n'
        xml_output += f"\t<AirfieldName>{icao}_AAFIF v1</AirfieldName>\n"
        xml_output += '\t<AFIDSet>false</AFIDSet>\n'

        
        return xml_output

    if runways:

        tt80_df = runways.get("intermediate_points")
        
        #HI THRESHOLD POINT row[''] 
        
        xml_output += '\t<TP_Runway>\n'
        xml_output += f"\t\t<RunwayName>RWY{runways['hi_ident']}</RunwayName>\n"
        xml_output += '\t\t<RunwayStartPoint>\n'
        xml_output += f"\t\t\t<Latitude>{tt80_df['latitude'].iloc[0]}</Latitude>\n"
        xml_output += f"\t\t\t<Longitude>{tt80_df['longitude'].iloc[0]}</Longitude>\n"
        xml_output += f"\t\t\t<Altitude>{round(runways['hi_elev_ft'] + runways['GSV_alt']):.0f}</Altitude>\n"
        xml_output += '\t\t</RunwayStartPoint>\n'
        xml_output += '\t\t<RunwayEndPoint>\n'
        xml_output += f"\t\t\t<Latitude>{tt80_df['latitude'].iloc[16]}</Latitude>\n"
        xml_output += f"\t\t\t<Longitude>{tt80_df['longitude'].iloc[16]}</Longitude>\n"
        xml_output += f"\t\t\t<Altitude>{round(runways['lo_elev_ft'] + runways['GSV_alt']):.0f}</Altitude>\n"
        xml_output += '\t\t</RunwayEndPoint>\n'
        xml_output += '\t\t<RunwayWidth>150</RunwayWidth>\n'
        xml_output += '\t\t<ThresholdOffset>\n'
        xml_output += '\t\t\t<Offset>\n'
        xml_output += '\t\t\t\t<dist>0</dist>\n'				
        xml_output += f"\t\t\t\t<elev>{round(runways['hi_elev_ft'] + runways['GSV_alt']):.0f}</elev>\n"			
        xml_output += '\t\t\t</Offset>\n'
        xml_output += f"\t\t\t<GSVFt>{runways['GSV_alt']}</GSVFt>\n"
        xml_output += '\t\t</ThresholdOffset>\n'

        for i, (tt80_idx, tt80_row) in enumerate(tt80_df.iloc[1:16].iterrows(), start=1):
            xml_output += '\t\t<RunwayIntermediatePoint>\n'
            xml_output += f"\t\t\t<dist>{round(tt80_row['distance_from_start_ft']):.0f}</dist>\n"
            xml_output += f"\t\t\t<elev>{round(tt80_row['ptEGM96alt']):.0f}</elev>\n"  
            xml_output += '\t\t</RunwayIntermediatePoint>\n'
        
        xml_output += '\t\t<TP_Approach>\n'
        xml_output += '\t\t\t<Profile>\n'
        xml_output += f"\t\t\t\t<Name>RWY_{runways['hi_ident']}_APP</Name>\n"
        xml_output += '\t\t\t\t<Coordinates>\n'	
        xml_output += f"\t\t\t\t\t<Latitude>{runways['APP_points'][0]}</Latitude>\n"		
        xml_output += f"\t\t\t\t\t<Longitude>{runways['APP_points'][1]}</Longitude>\n"
        xml_output += f"\t\t\t\t\t<Altitude>{round(runways['TP_Alt']):.0f}</Altitude>\n"
        xml_output += '\t\t\t\t</Coordinates>\n'
        xml_output += f"\t\t\t\t<AccelerationAltitude>{round(runways['TP_Alt']):.0f}</AccelerationAltitude>\n"
        xml_output += f"\t\t\t\t<ReleaseAltitude>{round(runways['TP_Alt']):.0f}</ReleaseAltitude>\n"
        xml_output += '\t\t\t\t<ReleaseDistance>0</ReleaseDistance>\n'		
        xml_output += f"\t\t\t\t<MinClearanceSlope>{runways['min_clnc_slope']}</MinClearanceSlope>\n"
        xml_output += '\t\t\t\t<LockState>Locked</LockState>\n'
        xml_output += '\t\t\t\t<DisplayGraphics>On</DisplayGraphics>\n'
        xml_output += '\t\t\t\t<ProfileShortName>\n'
        xml_output += f"\t\t\t\t\t<AirfieldShortName>{icao[-3:]}</AirfieldShortName>\n"
        xml_output += f"\t\t\t\t\t<RunwayShortName>{runways['hi_ident']}</RunwayShortName>\n"
        xml_output += '\t\t\t\t\t<PatternShortName>APP</PatternShortName>\n'
        xml_output += '\t\t\t\t</ProfileShortName>\n'
        xml_output += '\t\t\t</Profile>\n'
        xml_output += '\t\t\t<ApproachOffset>0</ApproachOffset>\n'
        xml_output += f"\t\t\t<GlideSlopeAngle>{runways['G_Slope']}</GlideSlopeAngle>\n"
        xml_output += f"\t\t\t<GlideSlopeAltitude>{round(runways['TP_Alt']):.0f}</GlideSlopeAltitude>\n"
        xml_output += f"\t\t\t<GoAroundAltitude>{round(runways['TP_Alt']):.0f}</GoAroundAltitude>\n"
        xml_output += f"\t\t\t<GoAroundSpeed>{runways['Go_Around_Spd']}</GoAroundSpeed>\n"
        xml_output += '\t\t\t<AltValidOffset>-3000</AltValidOffset>\n'
        xml_output += f"\t\t\t<StoppingDistance>{round(runways['STP_dist_ft']):.0f}</StoppingDistance>\n"
        xml_output += f"\t\t\t<ThresholdCrossingHeight>{round(runways['TCH']):.0f}</ThresholdCrossingHeight>\n"
        xml_output += '\t\t\t<FinalApproachPoint>\n'
        xml_output += f"\t\t\t\t\t<Latitude>{runways['APP_points'][0]}</Latitude>\n"	
        xml_output += f"\t\t\t\t\t<Longitude>{runways['APP_points'][1]}</Longitude>\n"
        xml_output += f"\t\t\t\t\t<Altitude>{round(runways['TP_Alt']):.0f}</Altitude>\n"
        xml_output += '\t\t\t</FinalApproachPoint>\n'
        xml_output += f"\t\t\t<TDDistanceFt>{round(runways['TD_dist_ft']):.0f}</TDDistanceFt>\n"
        xml_output += f"\t\t\t<TDRwyLeftFt>{round(runways['runway_remaining']):.0f}</TDRwyLeftFt>\n"
        xml_output += '\t\t</TP_Approach>\n'
        
        xml_output += '\t\t<TP_Departure>\n'
        xml_output += '\t\t\t<Profile>\n'
        xml_output += f"\t\t\t\t<Name>RWY_{runways['hi_ident']}_DEP</Name>\n"		
        xml_output += '\t\t\t\t<Coordinates>\n'				
        xml_output += f"\t\t\t\t\t<Latitude>{runways['DEP_points'][0]}</Latitude>\n"		
        xml_output += f"\t\t\t\t\t<Longitude>{runways['DEP_points'][1]}</Longitude>\n"
        xml_output += f"\t\t\t\t\t<Altitude>{round(runways['TP_Alt']):.0f}</Altitude>\n"
        xml_output += '\t\t\t\t</Coordinates>\n'		
        xml_output += f"\t\t\t\t<AccelerationAltitude>{round(runways['TP_Alt']):.0f}</AccelerationAltitude>\n"			
        xml_output += f"\t\t\t\t<ReleaseAltitude>{round(runways['TP_Alt']):.0f}</ReleaseAltitude>\n"
        xml_output += '\t\t\t\t<ReleaseDistance>0</ReleaseDistance>\n'		
        xml_output += f"\t\t\t\t<MinClearanceSlope>{runways['Min_Departure_Angle']}</MinClearanceSlope>\n"
        xml_output += '\t\t\t\t<LockState>Locked</LockState>\n'
        xml_output += '\t\t\t\t<DisplayGraphics>On</DisplayGraphics>\n'	
        xml_output += '\t\t\t\t<ProfileShortName>\n'
        xml_output += f"\t\t\t\t\t<AirfieldShortName>{icao[-3:]}</AirfieldShortName>\n"
        xml_output += f"\t\t\t\t\t<RunwayShortName>{runways['hi_ident']}</RunwayShortName>\n"
        xml_output += '\t\t\t\t\t<PatternShortName>DEP</PatternShortName>\n'
        xml_output += '\t\t\t\t</ProfileShortName>\n'
        xml_output += '\t\t\t</Profile>\n'
        xml_output += '\t\t</TP_Departure>\n'
        xml_output += '\t</TP_Runway>\n'
       
        
        return xml_output
              
    if finalize:

        #CLOSING TAGS
        xml_output += '</TerminalProcedure>\n'
        
        return xml_output

        
# xml_output += '<?xml version="1.0" encoding="UTF-8"?>\n'
# xml_output += '<TerminalProcedure xmlns:common="http://aero.lmco.com/adp/e3/common_types" xmlns:uci="http://uas-c2-initiative.mil/" xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xmlns:AAA="urn:us:gov:actdf" xmlns:AD="urn:us:gov:basic" xmlns:AB="urn:us:gov:ism" xmlns:AC="urn:us:gov:ism-cvenum" xmlns:tasking="urn:us:gov:tasking">\n'			
# xml_output += '\t<RunwaySurveyTimeStamp>2011-05-02T18:30:30Z</RunwaySurveyTimeStamp>\n'
# xml_output += '\t<RunwaySurveyVersion>361</RunwaySurveyVersion>\n'
# xml_output += '\t<Id>BFDFB6F4692341B2A22203FA3EF2CFA9</Id>\n'
# xml_output += '\t<State>Save</State>\n'
# xml_output += '\t<AFIDSet>false</AFIDSet>\n'
# xml_output += '\t<AirfieldName>KPIT_AAFIF v1</AirfieldName>\n'


# xml_output += '\t<TP_Runway>\n'
# xml_output += '\t\t<RunwayName>RWY10R</RunwayName>\n'
# xml_output += '\t\t<RunwayStartPoint>\n'
# xml_output += '\t\t\t<Latitude>40.48674166666679</Latitude>\n'
# xml_output += '\t\t\t<Longitude>-80.251913888888</Longitude>\n'
# xml_output += '\t\t\t<Altitude>1021</Altitude>\n'
# xml_output += '\t\t</RunwayStartPoint>\n'
# xml_output += '\t\t<RunwayEndPoint>\n'
# xml_output += '\t\t\t<Latitude>40.4856611111111</Latitude>\n'
# xml_output += '\t\t\t<Longitude>-80.2105972222222</Longitude>\n'
# xml_output += '\t\t\t<Altitude>1008</Altitude>\n'
# xml_output += '\t\t</RunwayEndPoint>\n'
# xml_output += '\t\t<RunwayWidth>150</RunwayWidth>\n'
# xml_output += '\t\t<ThresholdOffset>\n'
# xml_output += '\t\t\t<Offset>\n'
# xml_output += '\t\t\t\t<dist>0</dist>\n'				
# xml_output += '\t\t\t\t<elev>1021</elev>\n'				
# xml_output += '\t\t\t</Offset>\n'
# xml_output += '\t\t\t<GSVFt>-114</GSVFt>\n'
# xml_output += '\t\t</ThresholdOffset>\n'


# xml_output += '\t\t<RunwayIntermediatePoint>\n'
# xml_output += '\t\t\t<dist>123</dist>\n'
# xml_output += '\t\t\t<elev>1020</elev>\n'
# xml_output += '\t\t</RunwayIntermediatePoint>\n'


# xml_output += '\t\t<TP_Approach>\n'
# xml_output += '\t\t\t<Profile>\n'
# xml_output += '\t\t\t\t<Name>RWY_10R_APP</Name>\n'			
# xml_output += '\t\t\t\t<Coordinates>\n'	
# xml_output += '\t\t\t\t\t<Latitude>40.4894166264893</Latitude>\n'		
# xml_output += '\t\t\t\t\t<Longitude>-80.3567244070484</Longitude>\n'
# xml_output += '\t\t\t\t\t<Altitude>2600</Altitude>\n'
# xml_output += '\t\t\t\t</Coordinates>\n'
# xml_output += '\t\t\t\t<AccelerationAltitude>2600</AccelerationAltitude>\n'	
# xml_output += '\t\t\t\t<ReleaseAltitude>2600</ReleaseAltitude>\n'
# xml_output += '\t\t\t\t<ReleaseDistance>0</ReleaseDistance>\n'		
# xml_output += '\t\t\t\t<MinDistance>0</MinDistance>\n'	
# xml_output += '\t\t\t\t<MinClearanceSlope>2.5</MinClearanceSlope>\n'
# xml_output += '\t\t\t\t<LockState>Locked</LockState>\n'
# xml_output += '\t\t\t\t<DisplayGraphics>On</DisplayGraphics>\n'
# xml_output += '\t\t\t\t<ProfileShortName>\n'
# xml_output += '\t\t\t\t\t<AirfieldShortName>PIT</AirfieldShortName>\n'
# xml_output += '\t\t\t\t\t<RunwayShortName>10R</RunwayShortName>\n'
# xml_output += '\t\t\t\t\t<PatternShortName>APP</PatternShortName>\n'
# xml_output += '\t\t\t\t</ProfileShortName>\n'
# xml_output += '\t\t\t</Profile>\n'
# xml_output += '\t\t\t<ApproachOffset>0</ApproachOffset>\n'
# xml_output += '\t\t\t<GlideSlopeAngle>3</GlideSlopeAngle>\n'
# xml_output += '\t\t\t<GlideSlopeAltitude>2600</GlideSlopeAltitude>\n'
# xml_output += '\t\t\t<GoAroundAltitude>2600</GoAroundAltitude>\n'
# xml_output += '\t\t\t<GoAroundSpeed>125</GoAroundSpeed>\n'
# xml_output += '\t\t\t<AltValidOffset>-3000</AltValidOffset>\n'
# xml_output += '\t\t\t<StoppingDistance>500</StoppingDistance>\n'
# xml_output += '\t\t\t<ThresholdCrossingHeight>52</ThresholdCrossingHeight>\n'
# xml_output += '\t\t\t<FinalApproachPoint>\n'
# xml_output += '\t\t\t\t\t<Latitude>40.4894166264893</Latitude>\n'	
# xml_output += '\t\t\t\t\t<Longitude>-80.3567244070484</Longitude>\n'	
# xml_output += '\t\t\t\t\t<Altitude>2600</Altitude>\n'
# xml_output += '\t\t\t</FinalApproachPoint>\n'
# xml_output += '\t\t\t<TDDistanceFt>1000</TDDistanceFt>\n'
# xml_output += '\t\t\t<TDRwyLeftFt>10483.4420651856</TDRwyLeftFt>\n'
# xml_output += '\t\t</TP_Approach>\n'
# xml_output += '\t\t<TP_Departure>\n'
# xml_output += '\t\t\t<Profile>\n'
# xml_output += '\t\t\t\t<Name>RWY_10R_DEP</Name>\n'		
# xml_output += '\t\t\t\t<Coordinates>\n'				
# xml_output += '\t\t\t\t\t<Latitude>40.4827703784167</Latitude>\n'		
# xml_output += '\t\t\t\t\t<Longitude>-80.1012948119756</Longitude>\n'
# xml_output += '\t\t\t\t\t<Altitude>2600</Altitude>\n'
# xml_output += '\t\t\t\t</Coordinates>\n'		
# xml_output += '\t\t\t\t<AccelerationAltitude>2600</AccelerationAltitude>\n'			
# xml_output += '\t\t\t\t<ReleaseAltitude>2600</ReleaseAltitude>\n'
# xml_output += '\t\t\t\t<ReleaseDistance>0</ReleaseDistance>\n'		
# xml_output += '\t\t\t\t<MinDistance>0</MinDistance>\n'	
# xml_output += '\t\t\t\t<MinClearanceSlope>2</MinClearanceSlope>\n'
# xml_output += '\t\t\t\t<LockState>Locked</LockState>\n'
# xml_output += '\t\t\t\t<DisplayGraphics>On</DisplayGraphics>\n'	
# xml_output += '\t\t\t\t<ProfileShortName>\n'
# xml_output += '\t\t\t\t\t<AirfieldShortName>PIT</AirfieldShortName>\n'
# xml_output += '\t\t\t\t\t<RunwayShortName>10R</RunwayShortName>\n'
# xml_output += '\t\t\t\t\t<PatternShortName>DEP</PatternShortName>\n'
# xml_output += '\t\t\t\t</ProfileShortName>\n'
# xml_output += '\t\t\t</Profile>\n'
# xml_output += '\t\t</TP_Departure>\n'
# xml_output += '\t</TP_Runway>\n'


# xml_output += '</TerminalProcedure>\n'


