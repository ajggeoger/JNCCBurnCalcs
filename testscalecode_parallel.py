"""
This module contains code for testing the scaling up on JASMIN of calculating burn locations in Scotland, using data held on CEDA
    
Contributors: 
    Alastair Graham, Geoger Ltd, @ajggeoger
    Duncan Blake, Nature Scotland

"""

# Imports
#import logging
import os
import sys
import datetime
import json

import rasterio
#from dask_rasterio import read_raster, write_raster



def directorycheck(wd, od):
    '''
    Checks whether the supplied directories exist
    '''
    if os.path.isdir(wd) and os.path.isdir(od) == True:
        pass
    else:
        print('--EXITING--')
        print('one or more directories supplied do not exist')
        sys.exit()


def proclist(wd, jsonfile, testimages):
    '''
    creates a list of images for testing. 
    Takes in a working directory path, a json file of all test images,and a list of which images to process from the json.
    Returns a list of lists stating file names, paths and sizes.
    '''
    # TODO: Have this/a function read the files from the data directory in the operational code.... 
    with open(jsonfile) as json_file: 
        data = json.load(json_file)
    data   

    outlist = []
    for i in testimages:
        a = data[i]['date']
        year = a[0:4]
        month = a[4:6]
        day = a[6:]
        imagepath = (year + '/' + month + '/' + day)
        imagename = data[i]['name'] + '.tif'
        paramlist = (imagename, imagepath, data[i]['granule'], data[i]['datafile'])
        outlist.append(paramlist)

    #print(filename.count('_'))
    #sensor, date, latlon, granule, orbit, utm, proj, mask, sharp, radiative, srefdem, stdsref = filename.split('_')
    return outlist
    
# def predask(imagename):
#     red = read_raster(imagename, band=3)
#     nir = read_raster(imagename, band=7)
#     swir1 = read_raster(imagename, band=9)
#     swir2 = read_raster(imagename, band=10)
#     return red, nir, swir1, swir2

def pre(imagename):
    '''
    Opens and reads the pre fire image. 
    Takes in a path to a .tif file.
    Returns individual bands and the image profile.
    '''
    with rasterio.open(imagename) as dataset:
        print('PRE BURN IMAGE')
        print('Name: ', dataset.name)
        print('Count: ', dataset.count)
        print('Width: ', dataset.width)
        print('Height: ', dataset.height)
        print('CRS: ', dataset.crs)

        profile = dataset.profile.copy()

        red = dataset.read(3)
        nir = dataset.read(7)
        swir1 = dataset.read(9)
        swir2 = dataset.read(10)
        return red, nir, swir1, swir2, profile


def post(imagename):
    ''' 
    Opens and reads the post fire image. 
    Takes in a path to a .tif file.
    Returns individual bands and the image profile.
    '''
    with rasterio.open(imagename) as dataset:
        print('POST BURN IMAGE')
        print('Name: ', dataset.name)
        print('Count: ', dataset.count)
        print('Width: ', dataset.width)
        print('Height: ', dataset.height)
        print('CRS: ', dataset.crs)

        profile = dataset.profile.copy()

        red = dataset.read(3)
        nir = dataset.read(7)
        swir1 = dataset.read(9)
        swir2 = dataset.read(10)
        return red, nir, swir1, swir2, profile


def nbr(swir1, nir):
    '''
    Calculates Normalised Burn Ratio (NBR).
    The NBR equation is the opposite way round to normal but this is as recommended by Filiponi: to make the behavior of the indices consistent i.e. the values of all the indices increase if fire has occurred. 
    '''
    nbr = ((swir1 - nir)/(swir1 + nir)).astype(rasterio.float32)
    return nbr
    

def nbr2(swir2, swir1):
    '''
    Calculates NBR2
    '''
    nbr2 = ((swir2 - swir1)/(swir2 + swir1)).astype(rasterio.float32)
    return nbr2

def savi(nir, red, L = 0.5):
    '''
    Calculates Soil Adjusted Vegetation Index (SAVI) 
    The default version of paramer L is set to 0.5. Specify a value in the function call to over-ride this.
    '''
    savi = (-1 * (1.5 * ((nir - red) / (nir + red + L)))).astype(rasterio.float32)
    return savi


def savedata(od, nbr, profile, name):
    kwds = profile

    # Change the format driver for the destination dataset to
    #kwds['driver'] = 'GTiff'
    kwds['dtype'] = 'float32'
    kwds['count'] = 1

    # Add GeoTIFF-specific keyword arguments.
    #kwds['tiled'] = True
    #kwds['blockxsize'] = 256
    #kwds['blockysize'] = 256
    #kwds['compress'] = 'JPEG'
    outname = name + '.tif'

    with rasterio.open((os.path.join(od, outname)), 'w', **kwds) as dst_dataset:
        # Write data to the destination dataset.
        dst_dataset.write(nbr, 1)

    # TODO: Flexible output name
    # TODO: Multiple band write? 
    # TODO: np.seterr(divide='ignore', invalid = 'ignore' ) #ignore errors from calculating indices/ ratios#over= 'ignore', under = 'ignore' 



if __name__ == "__main__":
    
    # TODO: make sure logging is in place

    # Set working directory
    wd = '/home/al/sdaDocuments/ProjectFiles/Muirburn_TEMP'
    # Set output directory
    od = wd
    # Set path to jsonfile of images
    jsonfile = '/home/al/sdaDocuments/Code/geoger/github/JNCCBurnCalcs/testimages_T30VVJ.json'
    # Set testimages 
    testimages = ['TEST_21','TEST_22']
    
    directorycheck(wd, od)

    # Get data
    toprocess = proclist(wd, jsonfile, testimages)
    print(toprocess)
    
    
    #image_data = os.path.join(wd, toprocess[], toprocess[0])
    #print(image_data)


    # Start timer
    starttime1 = datetime.datetime.now()
    print('--STARTING PROCESSING--')


    cleanlist = []
    for j in toprocess:
        if 'GB' in j[3]:
            cleanlist.append(j)

    # If too few images for comparison, exit the program
    if len(cleanlist) < 2:
            print('--EXITING--')
            print('Too few images to process in test')
            sys.exit()

    #for k in reversed(cleanlist):
    
        #image_data = os.path.join(wd, k[1], k[0])
        #print(image_data)

    count = 1
#j = ['a','b','c','d','e']
    while len(cleanlist) > 0:
        print('--GETTING DATA--')

        if count == 1:
            postlist = cleanlist.pop()
            #print('post', post)
            # post-fire image
            postred, postnir, postswir1, postswir2, postprofile = post(os.path.join(wd, postlist[1], postlist[0]))
            #postred, postnir, postswir1, postswir2 = predask(os.path.join(wd, postlist[1], postlist[0]))
        
        
        count = 2
        prelist = cleanlist.pop()
        

        with rasterio.open(os.path.join(wd, prelist[1], prelist[0])) as dataset:
            print('PRE BURN IMAGE')
            print('Name: ', dataset.name)
            print('Count: ', dataset.count)
            print('CRS: ', dataset.crs)
            profile = dataset.profile.copy()


        # pre-fire image
        prered, prenir, preswir1, preswir2, preprofile = pre(os.path.join(wd, prelist[1], prelist[0]))
        #prered, prenir, preswir1, preswir2 = predask(os.path.join(wd, prelist[1], prelist[0]))

        #PROCESSING

        #print('--CALCULATING NBR--')
        #prenbr = nbr(preswir1, prenir)
        #print("Pre-NBR Shape: ", prenbr.shape)
        #postnbr = nbr(postswir1, postnir)
        #print("Post-NBR Shape: ", postnbr.shape)
        #dnbr = postnbr - prenbr


        print('--CALCULATING NBR2--')
        # Pre/post NBR2 difference
        dnbr2 = nbr2(postswir2, postswir1) - nbr2(preswir2, preswir1)


        print('--CALCULATING SAVI--')
        # Pre/post SAVI difference
        dsavi = savi(postnir, postred) - savi(prenir, prered)


        #TODO: Thresholding



        if len(cleanlist) >= 1:
            postlist = prelist
            postred, postnir, postswir1, postswir2, postprofile = prered, prenir, preswir1, preswir2, preprofile
    


    print('--WRITING OUTPUT--')
    #savedata(od, prenbr2, preprofile)
    savedata(od, dnbr2, preprofile, 'dnbr2')
    savedata(od, dsavi, preprofile, 'dsavi')
    #prof = profile # reuse profile from tests/data/RGB.byte.tif...
    #write_raster(os.path.join(od,'processed_image.tif'), dsavi, **prof)

    # Stop timer
    endtime1=datetime.datetime.now()
    deltatime1=endtime1-starttime1
    print(("Time to process:  {0}  hr:min:sec".format(deltatime1)))



# -- Notes --

#Combined: 
#dSAVI still shows reasonable separability with the other classes (especially snow to no snow) though with a little overlap with no cloud to cloud (which did not exist in the Cairngorms image pair). 
#With the two test areas combined the results are a bit confused but NBR or NBR2 probably show the best separability. 
#The following ruleset seemed to give quite good results for both Skye and the Cairngorms and utilised both sets of training data to set the thresholds: 
#dSAVI >= median value (0.2853) AND post fire NBR > =median value (0.2395) 
#And a secondary rule to remove issues of false positives at edges of clouds 
#dNBR2 >= 0.8 (NB those pixels meeting this criterium were removed). 
#As a test these thresholds were used on a third area – Lammer Law in the southern highlands – as some previous work had already mapped burn patches occurring between 20 September 2019 and 19 April 2020. 
# Of the 115 burn areas mapped 89 were identified automatically.  That’s 77% There were 23 additional polygons that did not intersect a mapped burn area. 
#However of these 13 are almost certainly burns (south east corner above). 
#Of the remaining ten: 
#4 could feasibly be burns (unfortunately no synchronous aerial photography to tell) 
#3 represented one area along a watercourse (reason unknown) 
#3 were area of water. 