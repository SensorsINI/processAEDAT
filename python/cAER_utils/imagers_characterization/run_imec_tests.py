# ############################################################
# python class that runs experiments and save data with IMEC
#  test facility
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
from __future__ import division
import numpy as np
import matplotlib
from pylab import *
import time, os
import shutil

# import caer communication and control labview instrumentations
import caer_communication
import labview_communication

#### SETUP PARAMETERS
caer_host = '127.0.0.1'
caer_port_command = 4040
caer_port_data =  7777
labview_host = '172.19.11.98'
labview_port = 5020
#### EXPERIMENT/CAMERA PARAMETERS
wavelengths = np.linspace(350, 800, 451)
exposures = np.linspace(1,1000000,100)
frame_number = 100 
global_shutter = True 
useinternaladc = True
datadir = 'measurements'
sensor = "DAVIS240C_" 
sensor_type ="DAVISFX2" 
bias_file = "cameras/davis240c_standards.xml" 
dvs128xml = False
current_date = time.strftime("%d_%m_%y-%H_%M_%S")

###############################################################################
# TEST SELECTIONS
###############################################################################
measure_qe = True

###############################################################################
# CONNECT TO MACHINES
###############################################################################
caer_control = caer_communication.caer_communication(host=caer_host, port_control=caer_port_command, port_data = caer_port_data)
labview_control = labview_communication.labview_communication(host=labview_host, port_control=labview_port)
            
try:
    os.stat(datadir)
except:
    os.mkdir(datadir) 

def copyFile(src, dest):
    try:
        shutil.copy(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print 'Error: %s' % e
    # eg. source or destination doesn't exist
    except IOError as e:
        print 'Error: %s' % e.strerror
        
###############################################################################
# RUN PROTOCOLS AND GATHER DATA
###############################################################################
if measure_qe:
    ################### Initialization #########################
    # Step I1: Check connection (Verify communication with the server)
    labview_control.open_communication_command()
    if(labview_control.check_connection() == False):
        print "Error I1: no connection to labview\n"
    else:
        print "Connected to labview\n"
        
        ################### Set offset #########################        
        # Step O1:  Close shutter (set dark measurement condition)
        labview_control.open_communication_command()
        if(labview_control.close_shutter() == False):
            print "Error O1: shutter not closed\n"
        else:
            print "Shutter closed for dark measurement\n"
        
            # Step O2: Check error (Verifies the error status of the QE setup control software)
            labview_control.open_communication_command()
            if(labview_control.check_for_errors() == True):
                print "Error O2: error in setup control software\n"
            else:
                print "No error reported in the setup\n"
                
                # Step O3: Set the power meter offset (sets the offset value to the current reading)
                labview_control.open_communication_command()
                float power_meter_offset = labview_control.set_reference_power_offset()
                print "Power meter offset is set to " + str(power_meter_offset)
                
                # Step O4: Check error (Verifies the error status of the QE setup control software)
                labview_control.open_communication_command()
                if(labview_control.check_for_errors() == True):
                    print "Error O4: error in setup control software\n"
                else:
                    print "No error reported in the setup\n"
                    print "Start PTC measurement in dark...\n"
                    
                    ################### PTC in dark #########################                     
                    # Step D1:  Close shutter (set dark measurement condition)
                    labview_control.open_communication_command()
                    if(labview_control.close_shutter() == False):
                        print "Error D1: shutter not closed\n"
                    else:
                        print "Shutter closed for dark measurement\n"
                        
                        # Step D2: Check error (Verifies the error status of the QE setup control software)
                        labview_control.open_communication_command()
                        if(labview_control.check_for_errors() == True):
                            print "Error D2: error in setup control software\n"
                        else:
                            print "No error reported in the setup\n"
                            
                            # Step D3:  Measure PTC of the chip in the dark.
                            if(useinternaladc):
                                ADCtype = "_ADCint"
                            else:
                                ADCtype = "_ADCext"
                            folder = datadir + '/'+ sensor + ADCtype +'_ptc_dark_' +  current_date
                            setting_dir = folder + str("/settings/")
                            print "\n"
                            print "Doing PTC measurements"
                            caer_control.open_communication_command()
                            caer_control.load_biases(xml_file=bias_file, dvs128xml=dvs128xml)
                            copyFile(bias_file, setting_dir+str("biases_ptc_all_exposures.xml") )
                            caer_control.get_data_ptc( folder = folder, frame_number = frame_number, exposures=exposures, global_shutter=global_shutter, sensor_type = sensor_type, useinternaladc = useinternaladc )
                            caer_control.close_communication_command()    
                            print "Data saved in " +  folder
                            
                            ################### chip PTC under light ####################                             
                            for this_wavelength in range(len(wavelength)):                            
                                # Step W1: Set the wavelength of interest
                                labview_control.open_communication_command()
                                labview_control.set_wavelength(wavelength[this_wavelength])
                                labview_control.open_communication_command()
                                print "Set wavelength to " + str(wavelength[this_wavelength]) + ", read " + str(labview_control.set_wavelength)
                            
                                # Step W2: Check error (Verifies the error status of the QE setup control software)
                                labview_control.open_communication_command()
                                if(labview_control.check_for_errors() == True):
                                    print "Error W2: error in setup control software\n"
                                else:
                                    print "No error reported in the setup\n"
                                
                                    # Step DL1:  Close shutter (set dark measurement condition)
                                    labview_control.open_communication_command()
                                    if(labview_control.close_shutter() == False):
                                        print "Error DL1: shutter not closed\n"
                                    else:
                                        print "Shutter closed for dark measurement\n"
                                    
                                        # Step DL2: Check error (Verifies the error status of the QE setup control software)
                                        labview_control.open_communication_command()
                                        if(labview_control.check_for_errors() == True):
                                            print "Error DL2: error in setup control software\n"
                                        else:
                                            print "No error reported in the setup\n"
                                        
                                            # Step DL3: Measure the dark signal of the reference diode
                                            labview_control.open_communication_command()
                                            float ref_diode_DL3 = labview_control.read_reference_power()
                                            print "The dark signal of the reference diode is " + str(ref_diode_DL3)
                                            
                                            # Step DL4: Check error (Verifies the error status of the QE setup control software)
                                            labview_control.open_communication_command()
                                            if(labview_control.check_for_errors() == True):
                                                print "Error DL4: error in setup control software\n"
                                            else:
                                                print "No error reported in the setup\n"
                                                
                                                # Step PR1:  Open shutter (set measurement condition under illumination)
                                                labview_control.open_communication_command()
                                                if(labview_control.open_shutter() == False):
                                                    print "Error PR1: shutter not open\n"
                                                else:
                                                    print "Shutter opened for measurement under illumination\n"
                                                    
                                                    # Step PR2: Check error (Verifies the error status of the QE setup control software)
                                                    labview_control.open_communication_command()
                                                    if(labview_control.check_for_errors() == True):
                                                        print "Error PR2: error in setup control software\n"
                                                    else:
                                                        print "No error reported in the setup\n"
                                                        
                                                        # Step PR3: Measure the photoexcitation level of the reference diode
                                                        labview_control.open_communication_command()
                                                        float ref_diode_PR3 = labview_control.read_reference_power()
                                                        print "The photoexcitation level of the reference diode is " + str(ref_diode_PR3)
                                                        
                                                        # Step PR4: Check error (Verifies the error status of the QE setup control software)
                                                        labview_control.open_communication_command()
                                                        if(labview_control.check_for_errors() == True):
                                                            print "Error PR4: error in setup control software\n"
                                                        else:
                                                            print "No error reported in the setup\n"
                                                            
                                                            # Step PR5:  Measure PTC of the chip under illumination.
                                                            if(useinternaladc):
                                                                ADCtype = "_ADCint"
                                                            else:
                                                                ADCtype = "_ADCext"
                                                            folder = datadir + '/'+ sensor + ADCtype +'_ptc_light_' +  current_date # to do: include wavelength
                                                            setting_dir = folder + str("/settings/")
                                                            print "\n"
                                                            print "Doing PTC measurements"
                                                            caer_control.open_communication_command()
                                                            caer_control.load_biases(xml_file=bias_file, dvs128xml=dvs128xml)
                                                            copyFile(bias_file, setting_dir+str("biases_ptc_all_exposures.xml") )
                                                            caer_control.get_data_ptc( folder = folder, frame_number = frame_number, exposures=exposures, global_shutter=global_shutter, sensor_type = sensor_type, useinternaladc = useinternaladc )
                                                            caer_control.close_communication_command()    
                                                            print "Data saved in " +  folder
                                                            
                                                            # Step PR6: Measure the photoexcitation level of the reference diode
                                                            labview_control.open_communication_command()
                                                            float ref_diode_PR6 = labview_control.read_reference_power()
                                                            print "The photoexcitation level of the reference diode is " + str(ref_diode_PR6)
                                                            
                                                            # Step PR7: Check error (Verifies the error status of the QE setup control software)
                                                            labview_control.open_communication_command()
                                                            if(labview_control.check_for_errors() == True):
                                                                print "Error PR7: error in setup control software\n"
                                                            else:
                                                                print "No error reported in the setup\n"
                
                
                
