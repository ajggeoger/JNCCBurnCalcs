"""
Summary: 
This module contains code for testing the scaling up on JASMIN of calculating burn locations in Scotland, using Sentinel 2 Analysis Ready Data held on CEDA.

Description:
This code takes in a working and output directory which is validated, and searches for new images (checking the images found against a saved list of previously processed images). The list of processed images is retrieved from a file that is saved in pickle format. The working directory is generated by a crawl of the working directory filesystem. 

The list of images is sorted by date. A check is made that images are larger than 1GB so that only full granules are used (partially covered granules throw up errors when the division is applied). A cleaned, sorted list of files is fed into functions that read the imagery (having checked they are for the same granule) as pre-burn and post-burn datasets and passes that to functions that calculate NBR, NBR2 and SAVI. These outputs are then thresholded to create a seed layer, ready for region growing. 

Finally the imagery datasets and logfiles are exported.

Contributors: 
    Alastair Graham, Geoger Ltd, @ajggeoger
    Duncan Blake, Nature Scotland

Possible things to do:
- look at cloud masking
- improve code around partial image cover granules 

"""

# --- Imports ---
import logging
import os
import sys
import datetime
import glob
import pickle
import copy

import numpy as np
import rasterio
from rasterio.features import sieve


# --- Functions ---
def directorycheck(wd, od):
    '''
    Checks whether the supplied directories exist. Exits if they do not.
    
    Return:
    Successful check

    Keyword arguments:
    wd -- workingdirectory
    od -- output directory
    '''
    if os.path.isdir(wd) and os.path.isdir(od) == True:
        pass
    else:
        print('--EXITING--')
        print('one or more directories supplied do not exist')
        sys.exit()



def picklecheck(od):
    '''
    Check if the pickle file exists i.e. the code has been previously run
    
    Return: 
    A list of previously processed images (which may be empty)

    Keyword arguments:
    od -- output directory
    '''
    if os.path.isfile(os.path.join(od, 'imagelist.pkl')):
        # if it exists, load it as proc_list
        infile = open(os.path.join(od, 'imagelist.pkl'),'rb')
        proc_list = pickle.load(infile)
        infile.close()
    else:
        # create proc_list if doesn't exist
        proc_list = []
    return proc_list


def cleanlistfunc(inputfiles, proc_list):
    '''
    Cleans the file list to make sure that duplication does not occur
    
    Return:
    Cleaned list of data to process

    Keyword arguments:
    inputfiles -- list of crawled input files
    proc_list -- list of previously processed images
    '''

    count = 0
    rem, index, x = [], [], []
    for f in inputfiles:
        count +=1
        index.append(count)
        for e in proc_list:
            if e[0]==f[0]:
                rem.append(count)
    
    #print('REM: INDEX', rem, index)
    p = [x for x in index if x not in rem]
    res_list = [inputfiles[i-1] for i in (p)] 
    return res_list #[::-1]


def getdatalist(wd, proc_list):
    '''
    Walks the supplied directory and finds the required imagery

    Return:
    Cleaned list of images to be processed on this run

    Keyword arguments:
    wd -- working directory
    proc_list -- list of previously processed images
    '''
    
    inputfiles = []

    for r, d, f in os.walk(wd):
        for name in glob.fnmatch.filter(f, '*vmsk_sharp_rad_srefdem_stdsref.tif'):
            # create [imagename, imagepath, granule, size, date]
            size = (os.stat(os.path.join(r, name)).st_size)/(1024*1024*1024)
            paramlist = [name, r, name.split('_')[3], size, name.split('_')[1]] # os.path.join(r, name)
            inputfiles.append(paramlist)
    
    # sort by granule and date
    inputfiles2 = sorted(sorted(inputfiles, key = lambda x : x[4]), key = lambda x : x[2], reverse = False)

    # call cleaning function
    res_list = cleanlistfunc(inputfiles2, proc_list)
    # print(res_list)
    return res_list


def pre(imagename):
    '''
    Opens and reads the pre fire image. 
    Takes in a path to a .tif file.
    
    Return:
    Individual bands and the image profile.

    Keyword arguments:
    imagename -- the path to the image to be processed
    '''
    with rasterio.open(imagename) as dataset:
        print('PRE BURN IMAGE')
        print('Name: ', dataset.name)
        print('Bands: ', dataset.count)
        print('Width: ', dataset.width)
        print('Height: ', dataset.height)
        print('CRS: ', dataset.crs)

        profile = dataset.profile.copy()

        red = dataset.read(3)
        nir = dataset.read(7)
        swir1 = dataset.read(9)
        swir2 = dataset.read(10)

        logging.debug('PRE image data read')
        return red, nir, swir1, swir2, profile


def post(imagename):
    ''' 
    Opens and reads the post fire image. 
    Takes in a path to a .tif file.
    
    Return:
    Individual bands and the image profile.

    Keyword arguments:
    imagename -- the path to the image to be processed
    '''

    with rasterio.open(imagename) as dataset:
        print('POST BURN IMAGE')
        print('Name: ', dataset.name)
        print('Bands: ', dataset.count)
        print('Width: ', dataset.width)
        print('Height: ', dataset.height)
        print('CRS: ', dataset.crs)

        profile = dataset.profile.copy()

        red = dataset.read(3)
        nir = dataset.read(7)
        swir1 = dataset.read(9)
        swir2 = dataset.read(10)

        logging.debug('POST image data read')
        return red, nir, swir1, swir2, profile


def nbr(swir1, nir):
    '''
    Calculates Normalised Burn Ratio (NBR).
    The NBR equation is the opposite way round to normal but this is as recommended by Filiponi: to make the behavior of the indices consistent i.e. the values of all the indices increase if fire has occurred. 

    Return:
    NBR image

    Keyword arguements:
    swir1 -- short wave infra-red 1 band 
    nir -- near infra-red band
    '''
    nbr = ((swir1 - nir)/(swir1 + nir)).astype(rasterio.float32)
    logging.debug('NBR calculated')
    return nbr
    

def nbr2(swir2, swir1):
    '''
    Calculates NBR2

    Return:
    NBR2 image

    Keyword arguements:
    swir2 -- short wave infra-red 2 band 
    swir1 -- short wave infra-red 1 band 
    '''
    nbr2 = ((swir2 - swir1)/(swir2 + swir1)).astype(rasterio.float32)
    logging.debug('NBR2 calculated')
    return nbr2

def savi(nir, red, L = 0.5):
    '''
    Calculates Soil Adjusted Vegetation Index (SAVI) 
    The default version of paramer L is set to 0.5. Specify a value in the function call to over-ride this.
    
    Return:
    SAVI image

    Keyword arguements:
    nir -- near infra-red band 
    red -- red band
    L -- equation parameter
    '''
    savi = (-1 * (1.5 * ((nir - red) / (nir + red + L)))).astype(rasterio.float32)
    logging.debug('SAVI calculated')
    return savi


def threshold_imgs(dsavi, postnbr, dnbr2, thresholds):
    '''
    Uses a specified dictionary of thresholds applied to three input images to create a layer of seed areas ready for region growing. 
    
    Return:
    Seed area array

    Keyword arguements:
    dsavi -- pre/post difference in SAVI  
    postnbr -- post NBR 
    dnbr2 -- pre/post difference in NBR2
    thresholds -- dictionary of thresholds - can be changed in __main__
    '''

    # Create a copy of the postnbr image and reset all values in output raster to 0
    reclassArray = postnbr.copy()
    reclassArray[np.where(reclassArray != 0)] = 0

    # where dsavi is greater than the median and post fire image NBR is greater than the mean 
    reclassArray[np.where((dsavi>=(thresholds['threshdsavi'])) & (postnbr>=(thresholds['threshpostnbr'])))] = 1 
    
    # attempt to solve issue of edges of clouds being falsely identified which have high values in dnbr2
    # rasterio function to exclude clumps of pixels smaller than 3.  Diagonally joined pixels are allowed.
    
    reclassArray[np.where(dnbr2>=(thresholds['threshdnbr2']))] = 0
    sievedArray = rasterio.features.sieve(reclassArray.astype(rasterio.uint8), size=3, connectivity=8)
    return sievedArray


def savedata(od, datafile, profile, name, prename, postname):
    '''
    Saves spatial data 
    
    Return:
    NA
    
    Keyword arguements:
    od -- output directory  
    nbr -- ??? 
    profile -- spatial data profile for rasterio
    name -- name of the dataset
    '''
    #create output base name
    prename = prename.split('_')
    postname = postname.split('_')

    kwds = profile
    
    if name != 'burnseed':

        # Change the format driver for the destination dataset to
        #kwds['driver'] = 'GTiff'
        kwds['dtype'] = 'float32'
        kwds['count'] = 1

        outname = prename[0] + prename[1] + prename[3] + prename[4] + '_' + postname[0] + postname[1] + postname[3] + postname[4] + '_' + name + '.tif'

        with rasterio.open((os.path.join(od, outname)), 'w', **kwds) as dst_dataset:
        # Write data to the destination dataset.
            dst_dataset.write(datafile, 1)

 
    else:
        #Export the thresholded raster
        kwds.update(dtype=rasterio.uint8,
            count=1,
            compress='lzw')
        outname = prename[0] + prename[1] + prename[3] + prename[4] + '_' + postname[0] + postname[1] + postname[3] + postname[4] + '_' + name + '.tif'

        with rasterio.open(os.path.join(od, outname), 'w', **kwds) as dst_dataset:
            dst_dataset.write(datafile, 1)





# ======================================================================    
# ========================== MAIN ======================================
# ======================================================================

if __name__ == "__main__":
    
    # Set working directory
    wd = '/home/al/sdaDocuments/ProjectFiles/Muirburn_TEMP/2019'
    
    # Set output directory
    od = wd
    
    # Set logfile 
    logfile = os.path.join(od, (datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+'-processing.log'))
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s %(message)s')

    # Check directory validity
    directorycheck(wd, od)
    logging.debug('Directories validated')


    # Get data and list of processed files
    proc_list = picklecheck(od)
    toprocess = getdatalist(wd, proc_list)


    print('Processing list constructed')
    logging.debug('Processing list constructed')
    logging.debug(toprocess)


    # Start timer
    starttime1 = datetime.datetime.now()
    print('--STARTING PROCESSING--')

    cleanlist = []
    # Look for full scenes: remove to process all images (what is effect of null data?)
    for j in toprocess:
        if j[3] > 1:
            cleanlist.append(j)


    # If too few images for comparison, exit the program
    if len(cleanlist) < 2:
            print('--EXITING--')
            print('Too few images to process in test')
            logging.error('Too few images supplied for processing')

            sys.exit()

    checklist = copy.deepcopy(cleanlist)

    
    count = 1
    while len(cleanlist) > 0:
        print('--GETTING DATA--')

        if count == 1:
            postlist = cleanlist.pop()
            #print('postlist: ', postlist)
            # post-fire image
            postred, postnir, postswir1, postswir2, postprofile = post(os.path.join(postlist[1], postlist[0]))
        
        
        count = 2
        prelist = cleanlist.pop()
        #print(prelist[2], postlist[2])

        # pre-fire image
        prered, prenir, preswir1, preswir2, preprofile = pre(os.path.join(prelist[1], prelist[0]))
        
        if prelist[2]==postlist[2]:

            #PROCESSING

            print('--CALCULATING postNBR--')
            #prenbr = nbr(preswir1, prenir)
            postnbr = nbr(postswir1, postnir)
            #dnbr = postnbr - prenbr


            print('--CALCULATING dNBR2--')
            # Pre/post NBR2 difference
            dnbr2 = nbr2(postswir2, postswir1) - nbr2(preswir2, preswir1)


            print('--CALCULATING dSAVI--')
            # Pre/post SAVI difference
            dsavi = savi(postnir, postred) - savi(prenir, prered)


            # Thresholding
            print('--CALCULATING THRESHOLDING--')
            thresholds = {'threshdsavi': 0.2853, 'threshpostnbr': 0.2395, 'threshdnbr2': 0.8, 'type': 'global'}
            print('Thresholds used: ', thresholds)
            burnseed = threshold_imgs(dsavi, postnbr, dnbr2, thresholds)


            # Save data
            print('--SAVING DATA--')
            savedata(od, postnbr, preprofile, 'postnbr', prelist[0], postlist[0])
            savedata(od, dnbr2, preprofile, 'dnbr2', prelist[0], postlist[0])
            savedata(od, dsavi, preprofile, 'dsavi', prelist[0], postlist[0])
            savedata(od, burnseed, preprofile, 'burnseed', prelist[0], postlist[0])
        


        if len(cleanlist) >= 1:
            postlist = prelist
            postred, postnir, postswir1, postswir2, postprofile = prered, prenir, preswir1, preswir2, preprofile
    


    print('--WRITING OUTPUT--')
    logging.debug('Writing output file')


    # pickle file
    checklist.pop()
    with open(os.path.join(od, 'imagelist.pkl'),'wb') as outfile:
        pickle.dump(checklist,outfile)
    
    # text file
    with open(os.path.join(od, 'imagelist.txt'), 'w') as outfiletxt:
        outfiletxt.writelines("%s" % line for line in checklist)



    # Stop timer
    endtime1=datetime.datetime.now()
    deltatime1=endtime1-starttime1
    print(("Time to process:  {0}  hr:min:sec".format(deltatime1)))
    logging.debug("Time to process:  {0}  hr:min:sec".format(deltatime1))



# TODO: np.seterr(divide='ignore', invalid = 'ignore' ) -- ignore errors from calculating indices/ ratios
