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
import caer_communication_imec
import labview_communication

#### SETUP PARAMETERS
caer_host = '127.0.0.1'
caer_port_command = 4040
caer_port_data =  7777
labview_host = '172.19.11.98'
labview_port = 5020
#### EXPERIMENT/CAMERA PARAMETERS
wavelengths = np.linspace(350, 800, 2)
exposures = np.linspace(1,2000,3)
frame_number = 100 
global_shutter = True 
useinternaladc = True
datadir = 'measurements'
sensor = "DAVIS346C" 
sensor_type ="DAVISFX3" 
bias_file = "cameras/davis346bsi_PTC.xml" 
dvs128xml = False
current_date = time.strftime("%d_%m_%y-%H_%M_%S")

###############################################################################
# TEST SELECTIONS
###############################################################################
measure_qe = True

###############################################################################
# CONNECT TO MACHINES
###############################################################################
caer_control = caer_communication_imec.caer_communication_imec(host=caer_host, port_control=caer_port_command, port_data = caer_port_data)
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
    log_dir = datadir+'/log/'
    if(not os.path.exists(log_dir)):
        os.makedirs(log_dir)
    log_file = log_dir + "log_imec_" + sensor + ".txt"
    out_file = open(log_file,"w")
    out_file.write(str(current_date) + "\n")

    ################### Initialization #########################
    out_file.write("################### Initialization #########################\n")
    # Step I1: Check connection (Verify communication with the server)
    labview_control.open_communication_command()
    if(labview_control.check_connection() == False):
        print "Error I1: no connection to labview\n"
        out_file.write("Error I1: no connection to labview\n")
    else:
        print "Connected to labview\n"
        out_file.write("Connected to labview\n")
        
        ################### Set offset #########################
        out_file.write("################### Set offset #########################\n")        
        # Step O1:  Close shutter (set dark measurement condition)
        labview_control.open_communication_command()
        if(labview_control.close_shutter() == False):
            print "Error O1: shutter not closed\n"
            out_file.write("Error O1: shutter not closed\n")
        else:
            print "Shutter closed for dark measurement\n"
            out_file.write("Shutter closed for dark measurement\n")
        
            # Step O2: Check error (Verifies the error status of the QE setup control software)
            labview_control.open_communication_command()
            if(labview_control.check_for_errors() == True):
                print "Error O2: error in setup control software\n"
                out_file.write("Error O2: error in setup control software\n")
            else:
                print "No error reported in the setup\n"
                out_file.write("No error reported in the setup\n")
                
                # Step O3: Set the power meter offset (sets the offset value to the current reading)
                labview_control.open_communication_command()
                power_meter_offset = labview_control.set_reference_power_offset()
                print "Power meter offset is set to " + str(power_meter_offset) + "\n"
                out_file.write("Power meter offset is set to " + str(power_meter_offset) + "\n")
                
                # Step O4: Check error (Verifies the error status of the QE setup control software)
                labview_control.open_communication_command()
                if(labview_control.check_for_errors() == True):
                    print "Error O4: error in setup control software\n"
                    out_file.write("Error O4: error in setup control software\n")
                else:
                    print "No error reported in the setup\n"
                    out_file.write("No error reported in the setup\n")
                                        
                    ################### chip PTC in dark #########################
                    out_file.write("################### chip PTC in dark #########################\n")
                    print "Start PTC measurement in dark...\n"
                    out_file.write("Start PTC measurement in dark...\n")
                    
                    # Step D1:  Close shutter (set dark measurement condition)
                    labview_control.open_communication_command()
                    if(labview_control.close_shutter() == False):
                        print "Error D1: shutter not closed\n"
                        out_file.write("Error D1: shutter not closed\n")
                    else:
                        print "Shutter closed for dark measurement\n"
                        out_file.write("Shutter closed for dark measurement\n")
                        
                        # Step D2: Check error (Verifies the error status of the QE setup control software)
                        labview_control.open_communication_command()
                        if(labview_control.check_for_errors() == True):
                            print "Error D2: error in setup control software\n"
                            out_file.write("Error D2: error in setup control software\n")
                        else:
                            print "No error reported in the setup\n"
                            out_file.write("No error reported in the setup\n")
                            
                            # Step D3:  Measure PTC of the chip in the dark.
                            if(useinternaladc):
                                ADCtype = "_ADCint"
                            else:
                                ADCtype = "_ADCext"
                            folder = datadir + '/'+ sensor + ADCtype +'_ptc_dark_' +  current_date
                            setting_dir = folder + str("/settings/")
                            if(not os.path.exists(setting_dir)):
                                os.makedirs(setting_dir)
                            print "Doing PTC measurements\n"
                            out_file.write("Doing PTC measurements\n")
                            caer_control.open_communication_command()
                            caer_control.load_biases(xml_file=bias_file, dvs128xml=dvs128xml)
                            copyFile(bias_file, setting_dir+str("biases_ptc_all_exposures.xml") )
                            caer_control.get_data_ptc(sensor, folder = folder, frame_number = frame_number, exposures=exposures, global_shutter=global_shutter, sensor_type = sensor_type, useinternaladc = useinternaladc )
                            caer_control.close_communication_command()    
                            print "Data saved in " +  folder + "\n"
                            out_file.write("Data saved in " +  folder + "\n")
                            
                            ################### chip PTC under light ####################
                            out_file.write("################### chip PTC under light #########################\n")
                            for this_wavelength in range(len(wavelengths)):                            
                                # Step W1: Set the wavelength of interest
                                out_file.write("----------------------------------------------------------------\n")
                                print "Setting wavelength to " + str(wavelengths[this_wavelength]) + "\n"
                                out_file.write("Setting wavelength to " + str(wavelengths[this_wavelength]) + "\n")
                                labview_control.open_communication_command()
                                wavelength_check = labview_control.set_wavelength(wavelengths[this_wavelength])
								#labview_control.open_communication_command()
								#wavelength_check = labview_control.read_wavelength
								#raise Exception
                                print "Wavelength is set to " + str(wavelength_check) + "\n"
                                out_file.write("Wavelength is set to " + str(wavelength_check) + "\n")
                                out_file.write("----------------------------------------------------------------\n")
                            
                                # Step W2: Check error (Verifies the error status of the QE setup control software)
                                labview_control.open_communication_command()
                                if(labview_control.check_for_errors() == True):
                                    print "Error W2: error in setup control software\n"
                                    out_file.write("Error W2: error in setup control software\n")
                                else:
                                    print "No error reported in the setup\n"
                                    out_file.write("No error reported in the setup\n")
                                
                                    # Step DL1:  Close shutter (set dark measurement condition)
                                    labview_control.open_communication_command()
                                    if(labview_control.close_shutter() == False):
                                        print "Error DL1: shutter not closed\n"
                                        out_file.write("Error DL1: shutter not closed\n")
                                    else:
                                        print "Shutter closed for dark measurement\n"
                                        out_file.write("Shutter closed for dark measurement\n")
                                    
                                        # Step DL2: Check error (Verifies the error status of the QE setup control software)
                                        labview_control.open_communication_command()
                                        if(labview_control.check_for_errors() == True):
                                            print "Error DL2: error in setup control software\n"
                                            out_file.write("Error DL2: error in setup control software\n")
                                        else:
                                            print "No error reported in the setup\n"
                                            out_file.write("No error reported in the setup\n")
                                        
                                            # Step DL3: Measure the dark signal of the reference diode
                                            labview_control.open_communication_command()
                                            ref_diode_DL3 = labview_control.read_reference_power()
                                            print "DL3: the dark signal of the reference diode is " + str(ref_diode_DL3)  + "\n"
                                            out_file.write("DL3: he dark signal of the reference diode is " + str(ref_diode_DL3)  + "\n")
                                            
                                            # Step DL4: Check error (Verifies the error status of the QE setup control software)
                                            labview_control.open_communication_command()
                                            if(labview_control.check_for_errors() == True):
                                                print "Error DL4: error in setup control software\n"
                                                out_file.write("Error DL4: error in setup control software\n")
                                            else:
                                                print "No error reported in the setup\n"
                                                out_file.write("No error reported in the setup\n")
                                                
                                                # Step PR1:  Open shutter (set measurement condition under illumination)
                                                labview_control.open_communication_command()
                                                if(labview_control.open_shutter() == False):
                                                    print "Error PR1: shutter not open\n"
                                                    out_file.write("Error PR1: shutter not open\n")
                                                else:
                                                    print "Shutter opened for measurement under illumination\n"
                                                    out_file.write("Shutter opened for measurement under illumination\n")
                                                    
                                                    # Step PR2: Check error (Verifies the error status of the QE setup control software)
                                                    labview_control.open_communication_command()
                                                    if(labview_control.check_for_errors() == True):
                                                        print "Error PR2: error in setup control software\n"
                                                        out_file.write("Error PR2: error in setup control software\n")
                                                    else:
                                                        print "No error reported in the setup\n"
                                                        out_file.write("No error reported in the setup\n")
                                                        
                                                        # Step PR3: Measure the photoexcitation level of the reference diode
                                                        labview_control.open_communication_command()
                                                        ref_diode_PR3 = labview_control.read_reference_power()
                                                        print "PR3: he photoexcitation level of the reference diode is " + str(ref_diode_PR3)  + "\n"
                                                        out_file.write("PR3: he photoexcitation level of the reference diode is " + str(ref_diode_PR3)  + "\n")
                                                        
                                                        # Step PR4: Check error (Verifies the error status of the QE setup control software)
                                                        labview_control.open_communication_command()
                                                        if(labview_control.check_for_errors() == True):
                                                            print "Error PR4: error in setup control software\n"
                                                            out_file.write("Error PR4: error in setup control software\n")
                                                        else:
                                                            print "No error reported in the setup\n"
                                                            out_file.write("No error reported in the setup\n")
                                                            
                                                            # Step PR5:  Measure PTC of the chip under illumination.
                                                            if(useinternaladc):
                                                                ADCtype = "_ADCint"
                                                            else:
                                                                ADCtype = "_ADCext"
                                                            folder = datadir + '/'+ sensor + ADCtype +'_ptc_wavelength_' + str(wavelengths[this_wavelength]) +  current_date
                                                            setting_dir = folder + str("/settings/")
                                                            if(not os.path.exists(setting_dir)):
                                                                os.makedirs(setting_dir)
                                                            print "Doing PTC measurements\n"
                                                            out_file.write("Doing PTC measurements\n")
                                                            caer_control.open_communication_command()
                                                            caer_control.load_biases(xml_file=bias_file, dvs128xml=dvs128xml)
                                                            copyFile(bias_file, setting_dir+str("biases_ptc_all_exposures.xml") )
                                                            caer_control.get_data_ptc(sensor, folder = folder, frame_number = frame_number, exposures=exposures, global_shutter=global_shutter, sensor_type = sensor_type, useinternaladc = useinternaladc )
                                                            caer_control.close_communication_command()    
                                                            print "Data saved in " +  folder + "\n"
                                                            out_file.write("Data saved in " +  folder + "\n")
                                                            
                                                            # Step PR6: Measure the photoexcitation level of the reference diode
                                                            labview_control.open_communication_command()
                                                            ref_diode_PR6 = labview_control.read_reference_power()
                                                            print "PR6: the photoexcitation level of the reference diode is " + str(ref_diode_PR6)  + "\n"
                                                            out_file.write("PR6: the photoexcitation level of the reference diode is " + str(ref_diode_PR6)  + "\n")
                                                            
                                                            # Step PR7: Check error (Verifies the error status of the QE setup control software)
                                                            labview_control.open_communication_command()
                                                            if(labview_control.check_for_errors() == True):
                                                                print "Error PR7: error in setup control software\n"
                                                                out_file.write("Error PR7: error in setup control software\n")
                                                            else:
                                                                print "No error reported in the setup\n"
                                                                out_file.write("No error reported in the setup\n")
                                                                
                                                                # Step DL5:  Close shutter (set dark measurement condition)
                                                                labview_control.open_communication_command()
                                                                if(labview_control.close_shutter() == False):
                                                                    print "Error DL5: shutter not closed\n"
                                                                    out_file.write("Error DL5: shutter not closed\n")
                                                                else:
                                                                    print "Shutter closed for dark measurement\n"
                                                                    out_file.write("Shutter closed for dark measurement\n")
                                                                
                                                                    # Step DL6: Check error (Verifies the error status of the QE setup control software)
                                                                    labview_control.open_communication_command()
                                                                    if(labview_control.check_for_errors() == True):
                                                                        print "Error DL6: error in setup control software\n"
                                                                        out_file.write("Error DL6: error in setup control software\n")
                                                                    else:
                                                                        print "No error reported in the setup\n"
                                                                        out_file.write("No error reported in the setup\n")
                                                                    
                                                                        # Step DL7: Measure the dark signal of the reference diode
                                                                        labview_control.open_communication_command()
                                                                        ref_diode_DL7 = labview_control.read_reference_power()
                                                                        print "DL7: the dark signal of the reference diode is " + str(ref_diode_DL3)  + "\n"
                                                                        out_file.write("DL7: he dark signal of the reference diode is " + str(ref_diode_DL3)  + "\n")
                                                                        
                                                                        # Step DL8: Check error (Verifies the error status of the QE setup control software)
                                                                        labview_control.open_communication_command()
                                                                        if(labview_control.check_for_errors() == True):
                                                                            print "Error DL8: error in setup control software\n"
                                                                            out_file.write("Error DL8: error in setup control software\n")
                                                                        else:
                                                                            print "No error reported in the setup\n"
                                                                            out_file.write("No error reported in the setup\n")
                                                                            print "Measurement completed for wavelength " + str(wavelengths[this_wavelength]) + "\n"
                                                                            out_file.write("Measurement completed for wavelength " + str(wavelengths[this_wavelength]) + "\n")

                                                                            ############### Compute average between DL3&7 and PR3&6 ###########################
    out_file.close()
                
                
                
