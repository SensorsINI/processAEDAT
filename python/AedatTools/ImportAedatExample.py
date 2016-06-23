# -*- coding: utf-8 -*-
"""
Created on Mon May 23 11:38:50 2016

@author: sim

Example script for how to invoke the ImportAedat function
"""

import sys
sys.path.append('C:\Users\Sim\Ini\JAER_SVN\scripts\python\ImportAedat')

import ImportAedat

# Create a dict with which to pass in the input parameters.
args = {}

# Put the filename, including full path, in the 'file' field.
args['filePathAndName'] = 'C:\\Users\\Sim\\example.aedat'

# Only read special events
args['dataTypes'] = {0}

# Invoke the function
output = ImportAedat.ImportAedat(args)
