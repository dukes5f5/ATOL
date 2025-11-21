# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 09:53:40 2025

@author: dukes
"""

def icao_kml(runways=None, icao=None, setup=False, finalize=False):
    
    kml_output = ''
    
    if setup:

        # with open(rf'C:\Users\dukes\Sync\AriesCI\ATOLv3_2025\RETURNS\{icao}\{icao}_SELECTED_RUNWAYS.kml', 'w') as kml_file:
        kml_output += '<?xml version="1.0" encoding="UTF-8"?>\n'
        kml_output += '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        kml_output += '<Document>\n'
        kml_output += f'\t<name>{icao}_SELECTED_RUNWAYS.kml</name>\n'
        kml_output += '\t<StyleMap id="m_ylw-pushpin">\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>normal</key>\n'
        kml_output += '\t\t\t<styleUrl>#s_ylw-pushpin</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>highlight</key>\n'
        kml_output += '\t\t\t<styleUrl>#s_ylw-pushpin_hl</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t</StyleMap>\n'
        kml_output += '\t<StyleMap id="msn_grn-blank">\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>normal</key>\n'
        kml_output += '\t\t\t<styleUrl>#sn_grn-blank</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>highlight</key>\n'
        kml_output += '\t\t\t<styleUrl>#sh_grn-blank</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t</StyleMap>\n'
        kml_output += '\t<StyleMap id="msn_grn-circle">\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>normal</key>\n'
        kml_output += '\t\t\t<styleUrl>#sn_grn-circle</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>highlight</key>\n'
        kml_output += '\t\t\t<styleUrl>#sh_grn-circle</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t</StyleMap>\n'
        kml_output += '\t<StyleMap id="msn_pink-square">\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>normal</key>\n'
        kml_output += '\t\t\t<styleUrl>#sn_pink-square</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>highlight</key>\n'
        kml_output += '\t\t\t<styleUrl>#sh_pink-square</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t</StyleMap>\n'
        kml_output += '\t<StyleMap id="msn_wht-blank">\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>normal</key>\n'
        kml_output += '\t\t\t<styleUrl>#sn_wht-blank</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>highlight</key>\n'
        kml_output += '\t\t\t<styleUrl>#sh_wht-blank</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t</StyleMap>\n'
        kml_output += '\t<Style id="s_ylw-pushpin">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<color>ff00ffff</color>\n'
        kml_output += '\t\t\t<scale>0.7</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        kml_output += '\t<Style id="s_ylw-pushpin_hl">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<color>ff00ffff</color>\n'
        kml_output += '\t\t\t<scale>0.7</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle_highlight.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        kml_output += '\t<Style id="sh_grn-blank">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>0.7</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/grn-blank.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t\t<ItemIcon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/grn-blank-lv.png</href>\n'
        kml_output += '\t\t\t</ItemIcon>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        kml_output += '\t<Style id="sh_grn-circle">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>0.7</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t\t<ItemIcon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/grn-circle-lv.png</href>\n'
        kml_output += '\t\t\t</ItemIcon>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        kml_output += '\t<Style id="sh_pink-square">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>0.7</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/pink-square.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t\t<ItemIcon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/pink-square-lv.png</href>\n'
        kml_output += '\t\t\t</ItemIcon>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        kml_output += '\t<Style id="sh_wht-blank">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>0.7</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t\t<ItemIcon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank-lv.png</href>\n'
        kml_output += '\t\t\t</ItemIcon>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        kml_output += '\t<Style id="sn_grn-blank">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>1.1</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/grn-blank.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t\t<ItemIcon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/grn-blank-lv.png</href>\n'
        kml_output += '\t\t\t</ItemIcon>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        kml_output += '\t<Style id="sn_grn-circle">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>1.1</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t\t<ItemIcon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/grn-circle-lv.png</href>\n'
        kml_output += '\t\t\t</ItemIcon>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        kml_output += '\t<Style id="sn_pink-square">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>1.1</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/pink-square.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t\t<ItemIcon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/pink-square-lv.png</href>\n'
        kml_output += '\t\t\t</ItemIcon>\n'
        kml_output += '\t\t</ListStyle>\n'
        
        kml_output += '\t</Style>\n'
        kml_output += '\t<Style id="sn_wht-blank">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>0.5</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t\t<ItemIcon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/wht-blank-lv.png</href>\n'
        kml_output += '\t\t\t</ItemIcon>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        #THRESHOLD PATH
        kml_output += '\t<StyleMap id="msn_ylw-pushpin">\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>normal</key>\n'
        kml_output += '\t\t\t<styleUrl>#sn_ylw-pushpin</styleUrl>\n'
        kml_output += '\t\tv</Pair>\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>highlight</key>\n'
        kml_output += '\t\t\t<styleUrl>#sh_ylw-pushpin</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t</StyleMap>\n'
        kml_output += '\t<Style id="sh_ylw-pushpin">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>1.3</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<LineStyle>\n'
        kml_output += '\t\t\t<color>ff0000ff</color>\n'
        kml_output += '\t\t</LineStyle>\n'
        kml_output += '\t</Style>\n'
        kml_output += '\t<Style id="sn_ylw-pushpin">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<scale>1.1</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t\t<hotSpot x="20" y="2" xunits="pixels" yunits="pixels"/>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<LineStyle>\n'
        kml_output += '\t\t\t<color>ff0000ff</color>\n'
        kml_output += '\t\t</LineStyle>\n'
        kml_output += '\t</Style>\n'
        
        #START STOP DIAMONDS
        kml_output += '\t<StyleMap id="msn_open-diamond">\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>normal</key>\n'
        kml_output += '\t\t\t<styleUrl>#sn_open-diamond0</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>highlight</key>\n'
        kml_output += '\t\t\t<styleUrl>#sh_open-diamond</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t</StyleMap>\n'
        kml_output += '\t<StyleMap id="msn_open-diamond0">\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>normal</key>\n'
        kml_output += '\t\t\t<styleUrl>#sn_open-diamond</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t\t<Pair>\n'
        kml_output += '\t\t\t<key>highlight</key>\n'
        
        kml_output += '\t\t\t<styleUrl>#sh_open-diamond0</styleUrl>\n'
        kml_output += '\t\t</Pair>\n'
        kml_output += '\t</StyleMap>\n'
        kml_output += '\t<Style id="sh_open-diamond">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<color>ff0000ff</color>\n'
        kml_output += '\t\t\t<scale>0.25</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        kml_output += '\t<Style id="sh_open-diamond0">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<color>ff00ff00</color>\n'
        kml_output += '\t\t\t<scale>0.25</scale>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        kml_output += '\t<Style id="sn_open-diamond">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t<color>ff00ff00</color>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        kml_output += '\t<Style id="sn_open-diamond0">\n' 
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '\t\t\t<color>ff0000ff</color>\n'
        kml_output += '\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href>\n'
        kml_output += '\t\t\t</Icon>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<BalloonStyle>\n'
        kml_output += '\t\t</BalloonStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        #ADD
        kml_output += '\t<Style id="sn_open-diamond">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '<color>ff00ff00</color>\n'
        kml_output += '<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href>\n'
        kml_output += '</Icon>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<LabelStyle>\n'
        kml_output += '<scale>0.7</scale>\n'
        kml_output += '\t\t</LabelStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        kml_output += '\t<Style id="sn_open-diamond0">\n'
        kml_output += '\t\t<IconStyle>\n'
        kml_output += '<color>ff0000ff</color>\n' #RED #AGBR
        kml_output += '<Icon>\n'
        kml_output += '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/open-diamond.png</href>\n'
        kml_output += '</Icon>\n'
        kml_output += '\t\t</IconStyle>\n'
        kml_output += '\t\t<LabelStyle>\n'
        kml_output += '<scale>0.7</scale>\n'
        kml_output += '\t\t</LabelStyle>\n'
        kml_output += '\t\t<ListStyle>\n'
        kml_output += '\t\t</ListStyle>\n'
        kml_output += '\t</Style>\n'
        
        #APP STAR STYLE
        kml_output += '\t\t<Style id="blueStar">\n'
        kml_output += '\t\t\t<IconStyle>\n'
        kml_output += '\t\t\t\t<color>ffff0000</color> <!-- Opaque blue in ABGR -->\n'
        kml_output += '\t\t\t\t<scale>1.2</scale>\n'
        kml_output += '\t\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/star.png</href>\n'
        kml_output += '\t\t\t\t</Icon>\n'
        kml_output += '\t\t\t</IconStyle>\n'
        kml_output += '\t\t</Style>\n'
        
        #APP PATH STYLE
        kml_output += '\t\t<Style id="blueLine">\n'
        kml_output += '\t\t\t<LineStyle>\n'
        kml_output += '\t\t\t\t<color>ffff0000</color> <!-- Opaque blue -->\n'
        kml_output += '\t\t\t\t<width>2</width>\n'
        kml_output += '\t\t\t</LineStyle>\n'
        kml_output += '\t\t</Style>\n'
        
        #DEP SQR STYLE
        kml_output += '\t\t<Style id="greenSquare">\n'
        kml_output += '\t\t\t<IconStyle>\n'
        kml_output += '\t\t\t\t<color>ff00ff00</color>\n'
        kml_output += '\t\t\t\t<scale>1.2</scale>\n'
        kml_output += '\t\t\t\t<Icon>\n'
        kml_output += '\t\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/square.png</href>\n'
        kml_output += '\t\t\t\t</Icon>\n'
        kml_output += '\t\t\t</IconStyle>\n'
        kml_output += '\t\t</Style>\n'
        
        #DEP PATH STYLE
        kml_output += '\t\t<Style id="greenLine">\n'
        kml_output += '\t\t\t<LineStyle>\n'
        kml_output += '\t\t\t\t<color>ff00ff00</color>\n' #<!-- Opaque blue -->
        kml_output += '\t\t\t\t<width>2</width>\n'
        kml_output += '\t\t\t</LineStyle>\n'
        kml_output += '\t\t</Style>\n'
                
        kml_output += '\t<Folder>\n'
        kml_output += f"\t\t<name>{icao} AFFIF Runways</name>\n"
        kml_output += '\t\t<open>1</open>\n'
        
        return kml_output

    if runways:

        tt80_df = runways.get("intermediate_points")
        
        #HI THRESHOLD POINT row[''] 
        
        
        kml_output += '<Folder>\n'
        kml_output += f"\t<name>RWY_{runways['hi_ident']}</name>\n"

        
        
        kml_output += '\t\t<Placemark>\n'
        kml_output += f"\t\t\t<name>{runways['hi_ident']}</name>\n"  #green_pin
        kml_output += '\t\t\t<LookAt>\n'
        kml_output += f"\t\t\t\t<longitude>{runways['hi_disp_thld_lat']}</longitude>\n"
        kml_output += f"\t\t\t\t<latitude>{runways['hi_disp_thld_long']}</latitude>\n"
        kml_output += '\t\t\t\t<altitude>0</altitude>\n'
        kml_output += '\t\t\t\t<heading>0.00</heading>\n'
        kml_output += '\t\t\t\t<tilt>0.00</tilt>\n'
        kml_output += '\t\t\t\t<range>2000</range>\n'
        kml_output += '\t\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>\n'
        kml_output += '\t\t\t</LookAt>\n'
        kml_output += '\t\t\t<styleUrl>#msn_grn-circle</styleUrl>\n'
        kml_output += '\t\t\t<Point>\n'
        kml_output += '\t\t\t\t<gx:drawOrder>1</gx:drawOrder>\n'
        kml_output += f"\t\t\t\t<coordinates>{runways['stpt_long']},{runways['stpt_lat']},0</coordinates>\n"
        kml_output += '\t\t\t</Point>\n'
        kml_output += '\t\t</Placemark>\n'
    
        #HI_WGS_LAT/LON row[''] 
        kml_output += '\t\t<Placemark>\n'
        kml_output += "\t\t\t<name></name>\n"  #white_pin
        kml_output += '\t\t\t<LookAt>\n'
        kml_output += f"\t\t\t\t<longitude>{runways['hi_disp_thld_long']}</longitude>\n"
        kml_output += f"\t\t\t\t<latitude>{runways['hi_disp_thld_lat']}</latitude>\n"
        kml_output += '\t\t\t\t<altitude>0</altitude>\n'
        kml_output += '\t\t\t\t<heading>0.00</heading>\n'
        kml_output += '\t\t\t\t<tilt>0.00</tilt>\n'
        kml_output += '\t\t\t\t<range>2000</range>\n'
        kml_output += '\t\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>\n'
        kml_output += '\t\t\t</LookAt>\n'
        kml_output += '\t\t\t<styleUrl>#msn_wht-blank</styleUrl>\n'
        kml_output += '\t\t\t<Point>\n'
        kml_output += '\t\t\t\t<gx:drawOrder>1</gx:drawOrder>\n'
        kml_output += f"\t\t\t\t<coordinates>{runways['hi_disp_thld_long']},{runways['hi_disp_thld_lat']},0</coordinates>\n"
        kml_output += '\t\t\t</Point>\n'
        kml_output += '\t\t</Placemark>\n'
        
        #TD_Point GREEN
        kml_output += '\t\t<Placemark>\n'
        kml_output += f"\t\t\t<name>{runways['TD_dist_ft']}</name>\n"
        kml_output += '\t\t\t<LookAt>\n'
        kml_output += '\t\t\t\t<longitude>-115.1234505755638</longitude>\n'
        kml_output += '\t\t\t\t<latitude>36.07643818169971</latitude>\n'
        kml_output += '\t\t\t\t<altitude>0</altitude>\n'
        kml_output += '\t\t\t\t<heading>0.0005154322149310232</heading>\n'
        kml_output += '\t\t\t\t<tilt>2.003337412069953</tilt>\n'
        kml_output += '\t\t\t\t<range>587.1897044361915</range>\n'
        kml_output += '\t\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>\n'
        kml_output += '\t\t\t</LookAt>\n'
        kml_output += '\t\t\t<styleUrl>#sn_open-diamond</styleUrl>\n' #GREEN
        kml_output += '\t\t\t<Point>\n'
        kml_output += '\t\t\t\t<gx:drawOrder>1</gx:drawOrder>\n'
        kml_output += f"\t\t\t\t<coordinates>{runways['TD_points'][1]},{runways['TD_points'][0]},0</coordinates>\n"
        kml_output += '\t\t\t</Point>\n'
        kml_output += '\t\t</Placemark>\n'
        
        # APP_Point & Path
        #APP STAR
        kml_output += '\t\t<Placemark>\n'
        kml_output += f"\t\t\t<name>APP_{runways['hi_ident']}_GS:{runways['G_Slope']:.1f}°</name>\n"
        kml_output += '\t\t\t<styleUrl>#blueStar</styleUrl>\n'
        kml_output += '\t\t\t<Point>\n'
        kml_output += f"\t\t\t\t<coordinates>{runways['APP_points'][1]},{runways['APP_points'][0]},0</coordinates>\n"
        kml_output += '\t\t\t</Point>\n'
        kml_output += '\t\t</Placemark>\n'
        
        #APP PATH
        kml_output += '\t\t<Placemark>\n'
        kml_output += '\t\t\t<name>Blue Path</name>\n'
        kml_output += '\t\t\t<styleUrl>#blueLine</styleUrl>\n'
        kml_output += '\t\t\t<LineString>\n'
        kml_output += '\t\t\t\t<coordinates>\n'
        kml_output += f"\t\t\t\t{runways['TD_points'][1]},{runways['TD_points'][0]},0\n"
        kml_output += f"\t\t\t\t{runways['APP_points'][1]},{runways['APP_points'][0]},0\n"
        kml_output += '\t\t\t\t</coordinates>\n'
        kml_output += '\t\t\t</LineString>\n'
        kml_output += '\t\t</Placemark>\n'
        
        # DEP_Point & Path
        #DEP STAR
        kml_output += '\t\t<Placemark>\n'
        kml_output += f"\t\t\t<name>DEP_{runways['hi_ident']}_DA:{runways['dep_climb_angle_deg']:.2f}°</name>\n"
        kml_output += '\t\t\t<styleUrl>#greenSquare</styleUrl>\n'
        kml_output += '\t\t\t<Point>\n'
        kml_output += f"\t\t\t\t<coordinates>{runways['DEP_points'][1]},{runways['DEP_points'][0]},0</coordinates>\n"
        kml_output += '\t\t\t</Point>\n'
        kml_output += '\t\t</Placemark>\n'
        
        #DEP PATH
        kml_output += '\t\t<Placemark>\n'
        kml_output += '\t\t\t<name>Blue Path</name>\n'
        kml_output += '\t\t\t<styleUrl>#greenLine</styleUrl>\n'
        kml_output += '\t\t\t<LineString>\n'
        kml_output += '\t\t\t\t<coordinates>\n'
        kml_output += f"\t\t\t\t{runways['lo_wgs_long']},{runways['lo_wgs_lat']},0\n"
        kml_output += f"\t\t\t\t{runways['DEP_points'][1]},{runways['DEP_points'][0]},0\n"
        kml_output += '\t\t\t\t</coordinates>\n'
        kml_output += '\t\t\t</LineString>\n'
        kml_output += '\t\t</Placemark>\n'
        
        #STP_Point RED
        kml_output += '\t\t<Placemark>\n'
        kml_output += f"\t\t\t<name>{runways['STP_dist_ft']}</name>\n"
        kml_output += '\t\t\t<LookAt>\n'
        kml_output += '\t\t\t\t<longitude>-115.1234505755638</longitude>\n'
        kml_output += '\t\t\t\t<latitude>36.07643818169971</latitude>\n'
        kml_output += '\t\t\t\t<altitude>0</altitude>\n'
        kml_output += '\t\t\t\t<heading>0.0005154322149310232</heading>\n'
        kml_output += '\t\t\t\t<tilt>2.003337412069953</tilt>\n'
        kml_output += '\t\t\t\t<range>587.1897044361915</range>\n'
        kml_output += '\t\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>\n'
        kml_output += '\t\t\t</LookAt>\n'
        kml_output += '\t\t\t<styleUrl>#sn_open-diamond0</styleUrl>\n' #RED
        kml_output += '\t\t\t<Point>\n'
        kml_output += '\t\t\t\t<gx:drawOrder>1</gx:drawOrder>\n'
        kml_output += f"\t\t\t\t<coordinates>{runways['STP_points'][1]},{runways['STP_points'][0]},0</coordinates>\n"
        kml_output += '\t\t\t</Point>\n'
        kml_output += '\t\t</Placemark>\n'
        
        #PATH
        kml_output += '\t\t<Placemark>\n'
        kml_output += '\t\t\t<name>Untitled Path</name>\n'
        kml_output += '\t\t\t<styleUrl>#msn_ylw-pushpin</styleUrl>\n'
        kml_output += '\t\t\t<LineString>\n'
        kml_output += '\t\t\t\t<tessellate>1</tessellate>\n'
        kml_output += f"\t\t\t\t<coordinates>{runways['hi_disp_thld_long']},{runways['hi_disp_thld_lat']},0 {runways['stpt_long']},{runways['stpt_lat']},0\n" 
        kml_output += '\t\t\t\t</coordinates>\n'
        kml_output += '\t\t\t</LineString>\n'
        kml_output += '\t\t</Placemark>\n'
        
        
        for i, (tt80_idx, tt80_row) in enumerate(tt80_df.iloc[1:16].iterrows(), start=1):
            if i == 8:
                kml_output += '\t\t<Placemark>\n'
                kml_output += (f"\t\t\t<name>LEN: {round(runways['total_distance_ft']) + round(runways['hi_disp_thld_ft'])}ft / " 
                                            f"HDG: {round(runways['rwy_hdg_mag'],1)}° / "
                                            f"SLP: {round(runways['rwy_slope_deg'],2)}°</name>\n"
                              )

                kml_output += '\t\t\t<LookAt>\n'
                kml_output += f"\t\t\t\t<longitude>{tt80_row['longitude']}</longitude>\n"
                kml_output += f"\t\t\t\t<latitude>{tt80_row['latitude']}</latitude>\n"
                kml_output += '\t\t\t\t<altitude>0</altitude>\n'
                kml_output += '\t\t\t\t<heading>0.0003241009972602429</heading>\n'
                kml_output += '\t\t\t\t<tilt>0.00</tilt>\n'
                kml_output += '\t\t\t\t<range>2000</range>\n'
                kml_output += '\t\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>\n'
                kml_output += '\t\t\t</LookAt>\n'
                kml_output += '\t\t\t<styleUrl>#m_ylw-pushpin</styleUrl>\n'
                kml_output += '\t\t\t<Point>\n'
                kml_output += '\t\t\t\t<gx:drawOrder>1</gx:drawOrder>\n'
                kml_output += f"\t\t\t\t<coordinates>{tt80_row['longitude']},{tt80_row['latitude']},0</coordinates>\n"
                kml_output += '\t\t\t</Point>\n'
                kml_output += '\t\t</Placemark>\n'
            else:

                kml_output += '\t\t<Placemark>\n'
                # kml_output += f'\t\t\t<name>{tt80_idx}</name>\n'
                kml_output += '\t\t\t<name></name>\n'
                kml_output += '\t\t\t<LookAt>\n'
                kml_output += f"\t\t\t\t<longitude>{tt80_row['longitude']}</longitude>\n"
                kml_output += f"\t\t\t\t<latitude>{tt80_row['latitude']}</latitude>\n"
                kml_output += '\t\t\t\t<altitude>0</altitude>\n'
                kml_output += '\t\t\t\t<heading>0.0003241009972602429</heading>\n'
                kml_output += '\t\t\t\t<tilt>0.00</tilt>\n'
                kml_output += '\t\t\t\t<range>2000</range>\n'
                kml_output += '\t\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>\n'
                kml_output += '\t\t\t</LookAt>\n'
                kml_output += '\t\t\t<styleUrl>#m_ylw-pushpin</styleUrl>\n'
                kml_output += '\t\t\t<Point>\n'
                kml_output += '\t\t\t\t<gx:drawOrder>1</gx:drawOrder>\n'
                kml_output += f"\t\t\t\t<coordinates>{tt80_row['longitude']},{tt80_row['latitude']},0</coordinates>\n"
                kml_output += '\t\t\t</Point>\n'
                kml_output += '\t\t</Placemark>\n'
    
        #END POINT row[''] 
        kml_output += '\t\t<Placemark>\n'
        kml_output += f"\t\t\t<name>{runways['lo_ident']}</name>\n"  #white_pin
        kml_output += '\t\t\t<LookAt>\n'
        kml_output += f"\t\t\t\t<longitude>{runways['lo_wgs_long']}</longitude>\n"
        kml_output += f"\t\t\t\t<latitude>{runways['lo_wgs_lat']}</latitude>\n"
        kml_output += '\t\t\t\t<altitude>0</altitude>\n'
        kml_output += '\t\t\t\t<heading>0.00</heading>\n'
        kml_output += '\t\t\t\t<tilt>0.00</tilt>\n'
        kml_output += '\t\t\t\t<range>2000</range>\n'
        kml_output += '\t\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>\n'
        kml_output += '\t\t\t</LookAt>\n'
        kml_output += '\t\t\t<styleUrl>#msn_pink-square</styleUrl>\n'
        kml_output += '\t\t\t<Point>\n'
        kml_output += '\t\t\t\t<gx:drawOrder>1</gx:drawOrder>\n'
        kml_output += f"\t\t\t\t<coordinates>{runways['lo_wgs_long']},{runways['lo_wgs_lat']},0</coordinates>\n"
        kml_output += '\t\t\t</Point>\n'
        kml_output += '\t\t</Placemark>\n'
        
        
        kml_output += '</Folder>\n'
        
        return kml_output
              
    if finalize:

        #CLOSING TAGS
        kml_output += '\t\t<atom:link rel="app" href="https://www.google.com/earth/about/versions/#earth-pro" title="Google Earth Pro 7.3.6.10201"></atom:link>\n'
        kml_output += '\t</Folder>\n'
        kml_output += '</Document>\n'
        kml_output += '</kml>\n'
        
        return kml_output

        
"""DEMO
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    "lat": [42.0, 42.1],
    "lon": [-88.0, -88.1]
})

# Manual and loop-generated arguments
manual_args = {"heading": 90.0}
loop_args = {f"marker_{i}": f"Point-{i}" for i in range(3)}

# Include the DataFrame
df_args = {"control_points": df}

# Merge all into one dictionary
all_args = {**manual_args, **loop_args, **df_args}

# Function that accepts **kwargs
def process_runway(**kwargs):
    print("Heading:", kwargs["heading"])
    print("Markers:", [v for k, v in kwargs.items() if k.startswith("marker_")])
    
    # Access the DataFrame
    control_df = kwargs.get("control_points")
    if isinstance(control_df, pd.DataFrame):
        print("Control Points DataFrame:")
        print(control_df)

process_runway(**all_args)
"""

