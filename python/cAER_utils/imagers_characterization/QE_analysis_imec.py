# ############################################################
# python class that analyses QE measurements of imec 
# author  Diederik Paul Moeys - diederikmoeys@live.com
# ############################################################
import sys
sys.path.append('utils/')
import load_files
sys.path.append('analysis/')
import APS_qe_slope
import matplotlib as plt
from pylab import *
import numpy as np
import os
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter


'''
in run imec test, name file with 0001000 or move the 1000 nm file at the
beginning in the ref diode file, otherwise numbers are offset and you make a 
mess when peaks occur
'''
#import winsound

#winsound.Beep(300,2000)

ioff()

################### 
# GET CHIP INFO
###################
#QE folder
directory_meas = ["C:/Users/Diederik Paul Moeys/Desktop/QE_DAVIS208_30_06_16-13_57_03/"]#,
#                  "C:/Users/Diederik Paul Moeys/Desktop/QE_DAVIS240C/"]
camera_file = ['cameras/davis208_parameters.txt']#,
#               'cameras/davis240c_parameters.txt']
               
QE = np.zeros([len(directory_meas),len(wavelengths),y_div,x_div])
sensor_name_list = []

for index_chip in range(len(directory_meas)):
    info = np.genfromtxt(camera_file[index_chip], dtype='str')
    sensor = info[0]
    # Replace this with measured conversion gain (with PTC measurements)
    if sensor == 'DAVISHet640':
        conv_gain_uve = 70.0
    elif sensor == 'DAVIS240C':
        conv_gain_uve = 20.0
    elif sensor == 'DAVIS208':
        conv_gain_uve = 20.0
    elif sensor == 'DAVIS346B':
        conv_gain_uve = 20.0
    elif sensor == 'DAVIS346C':
        conv_gain_uve = 20.0

    sensor_name_list.append(info[0])
    sensor_type =  info[1]
    bias_file = info[2]
    if(info[3] == 'False'):
        dvs128xml = False
    elif(info[3] == 'True'):
        dvs128xml == True
    host_ip = info[4]
    camera_dim = [int(info[5].split(',')[0].strip('[').strip(']')), int(info[5].split(',')[1].strip('[').strip(']'))]
    pixel_sel = [int(info[6].split(',')[0].strip('[').strip(']')), int(info[6].split(',')[1].strip('[').strip(']'))]
    ADC_range_int = float(info[7])
    ADC_range_ext = float(info[8])
    ADC_values = float(info[9])
    frame_x_divisions=[[0 for x in range(2)] for x in range(len(info[10].split(','))/2)]
    for x in range(0,len(info[10].split(',')),2):
        frame_x_divisions[x/2][0] = int(info[10].split(',')[x].strip('[').strip(']'))
        frame_x_divisions[x/2][1] = int(info[10].split(',')[x+1].strip('[').strip(']'))
    frame_y_divisions=[[0 for y in range(2)] for y in range(len(info[11].split(','))/2)]
    for y in range(0,len(info[11].split(',')),2):
        frame_y_divisions[y/2][0] = int(info[11].split(',')[y].strip('[').strip(']'))
        frame_y_divisions[y/2][1] = int(info[11].split(',')[y+1].strip('[').strip(']'))
    
    if sensor == 'DAVISHet640':
        pixel_area = (10.0*10**(-6))**2
    else:
        pixel_area = (18.5*10**(-6))**2
    
    y_div = len(frame_y_divisions)
    x_div = len(frame_x_divisions)
    
    ################### 
    # END PARAMETERS
    ###################
    
    wavelengths_in_dir = os.listdir(directory_meas[index_chip])
    wavelengths_in_dir.sort()
    aedat = APS_qe_slope.APS_qe_slope()
    
    wavelengths = np.zeros(len(wavelengths_in_dir))
    i_pd_vs = np.zeros([len(wavelengths_in_dir),y_div,x_div])+1*-1
    cg_uve = np.zeros([len(wavelengths_in_dir),y_div,x_div])+1*-1
    i_dark_vs = np.zeros([2,y_div,x_div])
    dark_count = 1
    
    for this_wavelength_file in range(len(wavelengths_in_dir)):
        if (wavelengths_in_dir[this_wavelength_file].lower().find('wavelength') > 0):
            ptc_dir = directory_meas[index_chip] + wavelengths_in_dir[this_wavelength_file] + "/"
            wavelengths[this_wavelength_file] = float(wavelengths_in_dir[this_wavelength_file].split('_')[4])
            print "processing PTC for wavelength " + str(wavelengths_in_dir[this_wavelength_file].split('_')[4]) + " nm"
            if('_ADCint' in ptc_dir):
                ADC_range = ADC_range_int
            else:
                ADC_range = ADC_range_ext
            i_pd_vs[this_wavelength_file,:,:], cg_uve[this_wavelength_file,:,:] = aedat.qe_slope_analysis(sensor, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values) # Photon transfer curve
            cg_uve[this_wavelength_file,:,:] = np.zeros([y_div,x_div])+1*conv_gain_uve
        elif (wavelengths_in_dir[this_wavelength_file].lower().find('dark') > 0):
            ptc_dir = directory_meas[index_chip] + wavelengths_in_dir[this_wavelength_file] + "/"
            print "processing PTC in dark # " + str(dark_count) + "/2"
            if('_ADCint' in ptc_dir):
                ADC_range = ADC_range_int
            else:
                ADC_range = ADC_range_ext
            i_dark_vs[dark_count-1,:,:] = aedat.qe_slope_analysis(sensor, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values) # Photon transfer curve for the dark
            dark_count = dark_count+1
            
    # Remove non-wavelengths
    files_num = len(wavelengths)
    to_remove = len(np.unique(np.where(wavelengths == 0)[0]))
    
    wavelengths_real = wavelengths[wavelengths != 0]
    wavelengths = np.reshape(wavelengths_real, (files_num-to_remove))
    
    i_pd_vs_real = i_pd_vs[i_pd_vs != -1]
    i_pd_vs = np.reshape(i_pd_vs_real, [files_num-to_remove, y_div, x_div])
    
    cg_uve_real = cg_uve[cg_uve != -1]
    cg_uve = np.reshape(cg_uve_real, [files_num-to_remove, y_div, x_div])
    
    # convert v/s per pixel to e/(s*m^2):
    #raise Exception
    i_pd_esm2 = np.zeros([len(wavelengths),y_div,x_div])
    for this_wavelength in range(len(wavelengths)):
        i_pd_esm2[this_wavelength, :, :] = ((i_pd_vs[this_wavelength, :, :] - (i_dark_vs[0,:,:]+i_dark_vs[1,:,:])/2)/(cg_uve[this_wavelength, :, :]/1000000.0))/pixel_area
    
    # Calculate QE
    p_ref_diode_wcm2 = np.zeros([len(wavelengths)]) #power density
    f_ref_diode_psm2 = np.zeros([len(wavelengths)]) #photon flux
    
    hc = 299792458.0*6.62607004*10**(-34.0)
    
    print "Looking for 'ref_diode_' file.."
    for files_in_folder in os.listdir(directory_meas[index_chip]):
        if files_in_folder.startswith("ref_diode_"):
            info_ref_diode = np.genfromtxt(directory_meas[index_chip]+files_in_folder, dtype='str')
            for this_wavelength in range(len(info_ref_diode)):
                p_d_light1 = float(info_ref_diode[this_wavelength].split('[')[3].split(';')[2])
                p_d_light2 = float(info_ref_diode[this_wavelength].split('[')[4].split(';')[2])
                p_d_dark1 = float(info_ref_diode[this_wavelength].split('[')[1].split(';')[2])
                p_d_dark2 = float(info_ref_diode[this_wavelength].split('[')[2].split(';')[2])
                p_ref_diode_wcm2[this_wavelength] = ((p_d_light1+p_d_light2)/2.0)-((p_d_dark1+p_d_dark2)/2.0)
                E_photon = hc/(wavelengths[this_wavelength]*10.0**(-9.0))
                f_ref_diode_psm2[this_wavelength] = (p_ref_diode_wcm2[this_wavelength]*10**(4))/E_photon
    
    #raise Exception
    for this_area_x in range(x_div):
        for this_area_y in range(y_div):
            QE[index_chip,:,this_area_y,this_area_x] = i_pd_esm2[:,this_area_y,this_area_x]/f_ref_diode_psm2
    
    # writing to report
    print "Writing report file.."
    report_file = directory_meas[index_chip]+"report_QE"+".txt"
    out_file = open(report_file,"w")
    for this_wavelength in range(len(wavelengths)):
        out_file.write("=========================================================\n")
        out_file.write("For wave length " + str(wavelengths[this_wavelength])+":\n")
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                out_file.write("X: " + str(frame_x_divisions[this_area_x]) + ", Y: " + str(frame_y_divisions[this_area_y]) + "\n")
                out_file.write("Pixel dark signal is: " + str(i_dark_vs[this_area_y,this_area_x]) + "V/s\n")
                out_file.write("Pixel total signal is: " + str(i_pd_vs[this_wavelength, this_area_y, this_area_x]) + "V/s\n")
                out_file.write("Pixel conversion gain is: " + str(cg_uve[this_wavelength, this_area_y, this_area_x]) + "uV/e\n")
                out_file.write("Pixel photo signal is: " + str(i_pd_esm2[this_wavelength, this_area_y, this_area_x]) + "e/(s*m^2)\n")
                out_file.write("Ref diode photo signal is: " + str(p_ref_diode_wcm2[this_wavelength]) + "W/(cm^2) or " + str(f_ref_diode_psm2[this_wavelength]) + "photons/(s*m^2)\n")
                out_file.write("Quantum efficiency is: " + str(QE[index_chip,this_wavelength, this_area_y, this_area_x]) + "\n")
                out_file.write("------------------------------------------------------\n")
    out_file.close()
#np.save(directory_meas[index_chip]+"/saved_variables/",QE,wavelengths,sensor_name_list,frame_x_divisions,frame_y_divisions)


# Plot
print "Plotting.."
figure_dir = directory_meas[index_chip]+'/figures_together/'
if(not os.path.exists(figure_dir)):
    os.makedirs(figure_dir)
# QE plot
fig = plt.figure()
ax = fig.add_subplot(111)
plt.title("Quantum Efficiency vs wavelength")
#wn, y_div, x_div = np.shape(QE)
colors = cm.rainbow(np.linspace(0, 1, x_div*y_div*len(directory_meas)))
color_tmp = 0;
#raise Exception
for index_chip in range(len(directory_meas)):
    for this_area_x in range(x_div):
        for this_area_y in range(y_div):
            index_fit = np.where(QE[index_chip,1:-1, this_area_y, this_area_x]!= 0)
            xx = np.linspace(wavelengths[index_fit[0][1]],wavelengths[index_fit[0][-1]], 1000)
            # interpolate + smooth
            itp = interp1d(wavelengths[1:-1],QE[index_chip,1:-1, this_area_y, this_area_x], kind='linear')
            window_size, poly_order = 101, 2
            yy_sg = savgol_filter(itp(xx), window_size, poly_order)
            plt.plot(wavelengths[1:-1], 100.0*(QE[index_chip,1:-1, this_area_y, this_area_x]), 'o--', color=colors[color_tmp], label='Chip: '+ str(sensor_name_list[index_chip])+', X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
            color_tmp = color_tmp+1
            plt.plot(xx, 100.0*yy_sg, 'k', label='Fit for chip: '+ str(sensor_name_list[index_chip])+', X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.xlabel('Wavelength [nm] ') 
plt.ylabel('Quantum Efficiency [%] ')
plt.savefig(figure_dir+"qe_wl.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
plt.savefig(figure_dir+"qe_wl.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
