# -*- coding: utf-8 -*-
"""
Created on Mon May 23 11:38:50 2016

@author: sim

Example script for how to invoke the ImportAedat function
"""

import sys
#sys.path.append('/home/federico/space/inilabs/data/multicam/cam0/')

import ImportAedat

# Create a dict with which to pass in the input parameters.
args = {}

# Put the filename, including full path, in the 'file' field.
#probelms caer_out-2016-06-23_17:24:47.aedat
args['filePathAndName'] = '/home/federico/space/inilabs/data/multicam/cam1/caer_out-2016-06-22_17_03_53_new.aedat'

# Read special events and polarity events
args['dataTypes'] = {0,1,2}

# Invoke the function
output = ImportAedat.ImportAedat(args)
