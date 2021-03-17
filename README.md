# OLD CODE:
This repo is now out of date. It contains legacy code that has been developed further and is now available from the following repository -
https://github.com/Scottish-Natural-Heritage/GIG-JNCC-Muirburn


# JNCCBurnCalcs
Code linked to the JNCC Muirburn project, designed to run on JASMIN using ARD from CEDA.

## Summary
This code is designed to run on a JASMIN Science Server (provided by the JNCC for this particular project). It is an initial attempt to scale up the use of Sentinel 2 (S2) Analysis Ready Data (ARD) - created by the JNCC and hosted on CEDA - for the purposes of mapping wildfire and muirburn areas in Scotland. The methodology for the assessment ofburn detection was provided by staff at Nature Scot and worked into the code in this repository.

There is an option to crawl a directory on CEDA and return the number of image granules in each sub-folder to be processed. If not required this can be commented out.

The code crawls a supplied directory and creates a list of valid tif files to be processed. It then filters the list against a list of previously processed images (imported from a pickle file, also available in raw text for ease of reading). This results in a list of new images to be processed, which is sorted by granule ID and date.

The code then creates image pairs for each granule - pre and post potential-burn images. These are used to create dnbr2, dSAVI and postnbr images which are then used in a thresholing process to create seed areas of possible burns.

Outputs are created using the following naming format:

* [IMG]	S2B20200627T31UCVORB094_S2B20200630T31UCVORB137_burnseed.tif	~2 MB	 
* [IMG]	S2B20200627T31UCVORB094_S2B20200630T31UCVORB137_dnbr2.tif	 	~275 MB	 
* [IMG]	S2B20200627T31UCVORB094_S2B20200630T31UCVORB137_dsavi.tif		~350 MB	 
* [IMG]	S2B20200627T31UCVORB094_S2B20200630T31UCVORB137_postnbr.tif	    ~300 MB

As can be seen the seed files are much smaller than the intermediate files. In an operational system the intermediate files should not be saved to disk. The output filenames take the form: 

** preburn image details _ postburn image details _ dataset type .tif **

where:
S2B = Sentinel satellite
20200627 = date in yyyymmdd format
T31UCV = granule ID
ORB094 = orbit ID

A shapefile is also output.


## How To
The code is presented as a single script (operationalcode.py) and configuration file (config.py). To run the code, log into the JASMIN Science Server and clone this repository. Navigate into the repository folder, change the details in the configuration file to match the system set up and run 'python operationalcode.py'.


## ToDo
* Investigate and add more robust error capturing to the code
* Investigate the use of parallel processing (either on the science server using tools such as dask or on the SLURM cluster batch compute on JASMIN)
* Improve thresholding values
* Refactor code into multiple files for ease of reading and debugging
