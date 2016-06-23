# ############################################################
# python class that analyses QE measurements of imec 
# author  Diederik Paul Moeys - diederikmoeys@live.com
# ############################################################
import sys
sys.path.append('utils/')
import load_files
sys.path.append('analysis/')
import APS_photon_transfer_curve
import matplotlib as plt
from pylab import *
import numpy as np
import os
import winsound

winsound.Beep(300,2000)

ioff()

################### 
# GET CHIP INFO
###################
#QE folder
directory_meas = "Z:/Characterizations/Measurements/QE_DAVIS346C_23_06_16-14_33_11/"
camera_file = 'cameras/davis346_parameters.txt'

info = np.genfromtxt(camera_file, dtype='str')
sensor = info[0]
sensor_type = info[1]
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
    
pixel_side_lenght = 18.0*10**(-6)
pixel_area = pixel_side_lenght*pixel_side_lenght

################### 
# END PARAMETERS
###################

wavelengths_in_dir = os.listdir(directory_meas)
wavelengths_in_dir.sort()
aedat = APS_photon_transfer_curve.APS_photon_transfer_curve()

wavelengths = np.zeros([len(wavelengths_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
QE = np.zeros([len(wavelengths_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
i_pd_es = np.zeros([len(wavelengths_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
i_dark_es = np.zeros([len(frame_y_divisions),len(frame_x_divisions)])
i_ref_diode_wcm = np.zeros([len(wavelengths_in_dir)])+1*-1
done = False

for this_wavelength_file in range(len(wavelengths_in_dir)):    
    ptc_dir = directory_meas + wavelengths_in_dir[this_wavelength_file] + "/"
    while(wavelengths_in_dir[this_wavelength_file].lower().find('wavelength') < 0):
        print "FILE" +str(this_wavelength_file)
        print "not a valid data file: " + str(wavelengths_in_dir[this_wavelength_file])
        if('_ADCint' in wavelengths_in_dir[this_wavelength_file]):
            ADC_range = ADC_range_int
        else:
            ADC_range = ADC_range_ext
        if(wavelengths_in_dir[this_wavelength_file].lower().find('dark') >= 0):
            print "PTC in dark processed"
#            i_dark_es= aedat.ptc_analysis(sensor, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values) # Photon transfer curve for the dark
        this_wavelength_file  = this_wavelength_file + 1
        if(this_wavelength_file == len(wavelengths_in_dir)):
            done = True
            break
    if(done == True):
        break
    wavelengths[this_wavelength_file] = float(wavelengths_in_dir[this_wavelength_file].split('_')[5])
    print "####################################"
    print "processing PTC for wavelength " + str(wavelengths_in_dir[this_wavelength_file].split('_')[5]) + " nm"
    i_pd_es[this_wavelength_file,:,:] = aedat.ptc_analysis(sensor, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values) # Photon transfer curve    


# Remove non-wavelengths
files_num, y_div, x_div = np.shape(wavelengths)
to_remove = len(np.unique(np.where(wavelengths == 0)[0]))
wavelengths_real = wavelengths[wavelengths != 0]
wavelengths = np.reshape(wavelengths_real, [files_num-to_remove, y_div, x_div])
QE_real = QE[QE != -1]
QE = np.reshape(QE_real, [files_num-to_remove, y_div, x_div])
i_ref_diode_wcm_real= i_ref_diode_wcm[files_num-to_remove]
i_ref_diode_wcm = np.reshape(i_ref_diode_wcm_real, [files_num-to_remove])

# Calculate QE
# i_pd_es is e/(s*(18um)^2) to convert to e/(s*cm^2):
i_pd_esm = (i_pd_es/pixel_area)*10^(-4)
print "Looking for 'ref_diode_' file.."
for files_in_folder in os.listdir(directory_meas):
    if files_in_folder.startswith("ref_diode_"):
        info_ref_diode = np.genfromtxt(directory_meas+files_in_folder, dtype='str')
        for this_wavelength in range(len(info_ref_diode)):
            i_d_light1 = float(info_ref_diode[this_wavelength].split('[')[3].split(';')[2])
            i_d_light2 = float(info_ref_diode[this_wavelength].split('[')[4].split(';')[2])
            i_d_dark1 = float(info_ref_diode[this_wavelength].split('[')[1].split(';')[2])
            i_d_dark2 = float(info_ref_diode[this_wavelength].split('[')[2].split(';')[2])
            i_ref_diode_wcm[this_wavelength_file] = ((i_d_light1+i_d_light2)/2.0)-((i_d_dark1+i_d_dark2)/2.0)
            # i_ref_diode_wcm is e/(s*(18um)^2) to convert to e/(s*cm^2):
            hc = 299792458.0*6.62607004*10^(-34.0)
            E_photon = hc/wavelengths[this_wavelength_file]
            i_ref_diode_pscm[this_wavelength_file] = (i_ref_diode_wcm*10^(4))/E_photon
            break

for this_wavelength_file in range(len(wavelengths_in_dir)):
    for this_area_x in range(x_div):
        for this_area_y in range(y_div):
            QE[this_wavelength_file,this_area_y,this_area_x] = (i_pd_esm[this_wavelength_file,this_area_y,this_area_x]-i_dark_es[this_area_y,this_area_x])/i_ref_diode_pscm[this_wavelength_file]

# Plot
figure_dir = directory_meas+'/figures/'
if(not os.path.exists(figure_dir)):
    os.makedirs(figure_dir)
# QE plot
fig = plt.figure()
ax = fig.add_subplot(111)
plt.title("Quantum Efficiency vs wavelength")
un, y_div, x_div = np.shape(u_y_tot)
colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
color_tmp = 0;
for this_area_x in range(x_div):
    for this_area_y in range(y_div):
        plt.plot( wavelengths[:,this_area_y,this_area_x], 100.0*(QE[:, this_area_y, this_area_x]), 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
        color_tmp = color_tmp+1
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.xlabel('Wavelength [nm] ') 
plt.ylabel('Quantum Efficiency [%] ')
plt.savefig(figure_dir+"qe_wlenght.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
plt.savefig(figure_dir+"qe_wlenght.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
