# -*- coding: utf-8 -*-
"""
Created on Mon May 23 11:38:50 2016

@author: sim

Example script for how to invoke the ImportAedat function
"""

import ImportAedat

# Create a dict with which to pass in the input parameters.
args = {}

# Put the filename, including full path, in the 'file' field.
args['filePathAndName'] = '/home/sim/Recordings/Laser_Scanning_Prj/Dungeon/ActiveRail/2016_05_20_laser_on_calibration_targets_and_rails/laser_rail-2016-05-18_13:50:17.aedat'

# Only read special events
args['dataTypes'] = {0}

# Invoke the function
output = ImportAedat.ImportAedat(args)
