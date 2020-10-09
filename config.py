"""
This module contains configuration information for use in the code for running on JASMIN to calculate burn locations in Scotland, using data held on CEDA
    
Contributors: 
    Alastair Graham, Geoger Ltd, @ajggeoger

"""
# Main set up
ARD_TOPDIR = '/neodc/sentinel_ard/data/'   # Input ARD data  
GWS = '/gws/nopw/j04/jncc_muirburn'        # Group workspace
SCOT_IMG = 'scottish_granules.txt'         # List of Scottish S2 granules
BURN_OUT = ''
LOGLOC = ''

CLOUD = 0.9 # Cloud cover threshold
