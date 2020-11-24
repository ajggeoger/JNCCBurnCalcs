"""
This module contains configuration information for use in the code for running on JASMIN to calculate burn locations in Scotland, using data held on CEDA
    
Contributors: 
    Alastair Graham, Geoger Ltd, @ajggeoger

"""
# --Main set up--
ARD_WRKDIR = '/home/al/sdaDocuments/ProjectFiles/Muirburn_TEMP/2019'           # Input ARD data  
GWS = '/gws/nopw/j04/jncc_muirburn'                                            # Group workspace
GWS_DATA = '/home/al/sdaDocuments/ProjectFiles/Muirburn_TEMP/output_data'      # GWS output location
LANDMASK = '/home/al/sdaDocuments/ProjectFiles/Muirburn_TEMP/incoming_data/scotland_mask_1bit.tif' # Land mask 1bit

# --Other parameters--
# Image thresholding values - the variable names are set in the code, but the values can be changed here.
# The type is a helper variable so that users know how it is being applied (global == to all images). 
THRESHOLD = {'threshdsavi': 0.2853, 'threshpostnbr': 0.2395, 'threshdnbr2': 0.8, 'type': 'global'}

# Image thresholding values - the variable names are set in the code, but the values can be changed here.
# The type is a helper variable so that users know how it is being applied (global == to all images). 
GROW = {'dsaviq1thresh': 0.206748, 'postnbrq1thresh': 0.173447, 'cloudthresh': 0.8, 'type': 'global'}


# Toggle the file count function on and off. Value can be 'off' or 'on'
FILECOUNT = 'off'

# Cloud cover threshold (for use in future versions: this is not called in the current code)
#CLOUD = 0.9 

# Granule filter - only process the granules listed in PROC_GRANULES. This list is those granules covering Scotland. 
PROC_GRANULES = ['T29UPB', 'T29VNC', 'T29VND', 'T29VNE', 'T29VNF', 'T29VPC', 'T29VPD', 'T29VPE', 'T29VPF', 'T29VPG', 'T30UUF', 'T30UUG', 'T30UVF', 'T30UVG', 'T30UWF', 'T30UWG', 'T30VUH', 'T30VUJ', 'T30VUK', 'T30VUL', 'T30VUM', 'T30VVH', 'T30VVJ', 'T30VVK', 'T30VVL', 'T30VVM', 'T30VVN', 'T30VWH', 'T30VWJ', 'T30VWK', 'T30VWL', 'T30VWM', 'T30VWN', 'T30VXH', 'T30VXJ', 'T30VXK', 'T30VXL', 'T30VXM', 'T30VXN', 'T31VCG', 'T31VCH']

# Date filter for seasonality. The code ignores those months listed in MONTHS_OUT 
# e.g. do not process 01 Sept - 31 dec inclusive
MONTHS_OUT = ['09', '10', '11', '12']


