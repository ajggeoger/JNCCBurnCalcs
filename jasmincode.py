"""
This module contains code for running on JASMIN to calculate burn locations in Scotland, using data held on CEDA
    
Contributors: 
    Alastair Graham, Geoger Ltd, @ajggeoger

"""

# Imports
import json
import pandas as pd

import importlib
import logging

import config

# Functions
def setup():
    """
    A simple function to import the script parameters from config.py 
    """
    importlib.reload(config)
    return config.ARD_TOPDIR, config.GWS, config.SCOT_IMG, config.BURN_OUT, config.LOGLOC, config.CLOUD


def scotIm(parameters):
    """
    A helper function to filter the CEDA ARD list so that only Scottish images are used
    """
    pass

    # Change this code
    #try:
    #    with open(scotlist) as f:
    #        print(f.readlines())
    #        # Do something with the file
    #except IOError:
    #    print("File not accessible")

def cloudIm(parameters):
    """
    A helper function to filter the CEDA ARD list for cloud cover
    """
    pass

def getARDlist(ardloc, startdate):
    """
    A helper function to filter the CEDA ARD list so that only Scottish images are used
    """
    pass
    # walk through ardloc to create a list of data that's on there, starting from startdate
    # call scotIm and cloudIm to filter



# Main program
if __name__ == "__main__":
    # get setup details
    ardloc, gws, scotlist, outloc, logs, cloud = setup()
    print('worked', gws, cloud)
    # get list of images to process
    # check whether this is the first run or not by looking for a pickled dictionary of ARD images

    