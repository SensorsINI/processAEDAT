# ############################################################
# python class that deals with cAER aedat3 file format
# and calculates PHOTON TRANSFER CURVE of APS
# author  Federico Corradi - federico.corradi@inilabs.com
# author  Diederik Paul Moeys - diederikmoeys@live.com
# 
# 25th Mmay 2016 - Tested by ChengHan
#
# ############################################################
from __future__ import division
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from pylab import *
sys.path.append('utils/')
import load_files
#import winsound

class APS_qe_slope:
    def qe_slope_analysis(self, sensor, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values):
        '''
            Photon transfer curve and sensitivity plot
         
        '''    
        figure_dir = ptc_dir+'/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        #pixel_area = (18e-6*18e-6)
        directory = ptc_dir
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()
        u_y_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
        exposures = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        Gain_uVe_lin = np.zeros([len(frame_y_divisions),len(frame_x_divisions)])
        i_pd_es = np.zeros([len(frame_y_divisions),len(frame_x_divisions)])
        i_pd_vs = np.zeros([len(frame_y_divisions),len(frame_x_divisions)])
        all_frames = []
        done = False

        for this_file in range(len(files_in_dir)):
            print "####################################"
            print("processing gray values from file ", str(files_in_dir[this_file]))
            while( not files_in_dir[this_file].endswith(".aedat")):
                print("not a valid data file ", str(files_in_dir[this_file]))
                this_file  = this_file + 1
                if(this_file == len(files_in_dir)):
                    done = True
                    break
            if(done == True):
                break
            shutter_type, exp = files_in_dir[this_file].strip(".aedat").strip("ptc_").strip("shutter_").split("_") # in us
            exp = float(exp)
            loader = load_files.load_files()
            [frame, xaddr, yaddr, pol, ts, sp_type, sp_t] = loader.load_file(directory+files_in_dir[this_file])

            #rescale frame to their values and divide the test pixels areas
            #for this_frame in range(len(frame)):
            for this_div_x in range(len(frame_x_divisions)) :
                for this_div_y in range(len(frame_y_divisions)): 
                    if sensor == 'DAVISHet640':           
                        frame_areas = [frame[this_frame][frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1]:2, frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]:2] for this_frame in range(len(frame))]
                    else:
                        frame_areas = [frame[this_frame][frame_y_divisions[this_div_y][0]:frame_y_divisions[this_div_y][1], frame_x_divisions[this_div_x][0]:frame_x_divisions[this_div_x][1]] for this_frame in range(len(frame))]
                    all_frames.append(frame_areas)
                    frame_areas = np.right_shift(frame_areas,6)
                    n_frames, ydim, xdim = np.shape(frame_areas)   
                    ydim_f , xdim_f = np.shape(frame_areas[0])
                    temporal_mean = np.zeros([ydim_f, xdim_f])
                    spatio_temporal_mean = np.mean(np.mean(temporal_mean,0),0)
                    u_y_tot[this_file, this_div_y, this_div_x] = spatio_temporal_mean
                    exposures[this_file, this_div_y, this_div_x] = exp
                            
        if(ptc_dir.lower().find('debug') < 0):        
            #just remove entry that corresponds to files that are not measurements
            files_num, y_div, x_div = np.shape(exposures)
            to_remove = len(np.unique(np.where(exposures == 0)[0]))
            exposures_real = exposures[exposures != 0]
            exposures = np.reshape(exposures_real, [files_num-to_remove, y_div, x_div])
            u_y_tot_real = u_y_tot[u_y_tot != -1]
            u_y_tot =  np.reshape(u_y_tot_real, [files_num-to_remove, y_div, x_div])
            exposures = exposures[:,0,0]
        
            # Sensitivity plot 
            plt.figure()
            plt.title("Sensitivity APS")
            un, y_div, x_div = np.shape(u_y_tot)
            colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
            color_tmp = 0;
            for this_area_x in range(x_div):
                for this_area_y in range(y_div):
                    plt.plot( exposures[:], u_y_tot[:,this_area_y,this_area_x], 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
                    color_tmp = color_tmp+1
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.xlabel('Exposure time [us]') 
            plt.ylabel('Mean[DN]') 
            plt.savefig(figure_dir+"sensitivity.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
            plt.savefig(figure_dir+"sensitivity.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
            # Sensitivity fit
            print("Sensitivity fit...")
            fig = plt.figure()
            ax = fig.add_subplot(111)
            slope = 0
            inter = 0
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            un, y_div, x_div = np.shape(u_y_tot)
            colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
            color_tmp = 0;
            percentage_margin = 0.2
            for this_area_x in range(x_div):
                for this_area_y in range(y_div):
                    range_sensitivity = np.max(u_y_tot[:,this_area_y,this_area_x]) - np.min(u_y_tot[:,this_area_y,this_area_x])
                    max80perc = np.max(u_y_tot[:,this_area_y,this_area_x]) - range_sensitivity*percentage_margin
                    indmax80perc = np.where(u_y_tot[:,this_area_y,this_area_x]  >= max80perc)[0][0]
                    min20perc = np.min(u_y_tot[:,this_area_y,this_area_x]) + range_sensitivity*percentage_margin
                    indmin20perc = np.where(u_y_tot[:,this_area_y,this_area_x]  >= min20perc)[0][0]
                    u_y_fit = u_y_tot[indmin20perc:indmax80perc,this_area_y, this_area_x]
                    exposures_t = np.array(exposures.reshape(len(exposures)))
                    exposures_fit = exposures_t[indmin20perc:indmax80perc]
                    try: 
                        slope, inter = np.polyfit(exposures_fit.reshape(len(exposures_fit)), u_y_fit.reshape(len(u_y_fit)),1)
                        fit_fn = np.poly1d([slope, inter])
                        i_pd_es[this_area_y,this_area_x] = slope*1000000.0*(ADC_range/ADC_values)/(Gain_uVe_lin[this_area_y,this_area_x]/1000000.0)
                        i_pd_vs[this_area_y,this_area_x] = slope*1000000.0*(ADC_range/ADC_values)
                        print "Photodiode current is: " + str(slope*1000000.0) + " DN/s or " + str(i_pd_es[this_area_y,this_area_x]) + " e/s or " + str(i_pd_vs[this_area_y,this_area_x]) + " V/s or " + str(i_pd_es[this_area_y,this_area_x]*1.6*10**(-19)) + " A for X: " + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y])
                        ax.plot(exposures_t, u_y_tot[:,this_area_y, this_area_x], 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) +' photodiode current: '+ str(format(i_pd_es[this_area_y,this_area_x], '.2f')) + ' e/s or ' + str(format(i_pd_vs[this_area_y,this_area_x], '.2f')) + ' V/s ')
                        ax.plot(exposures_t, fit_fn(exposures_t), '-*', markersize=4, color=colors[color_tmp])
                    except ValueError:
                        print("Poly Fit Failed for this recording.. skipping")
                        continue
                    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=2)
                    color_tmp = color_tmp+1
            color_tmp = 0;
            if(ptc_dir.lower().find('dark') < 0):
                plt.ylim([np.min(u_y_tot[:,this_area_y, this_area_x])-100,np.max(u_y_tot[:,this_area_y, this_area_x])+100])
            for this_area_x in range(len(frame_x_divisions)):
                for this_area_y in range(len(frame_y_divisions)):
                    ax.text( ax.get_xlim()[1]+((ax.get_xlim()[1]-ax.get_xlim()[0])/10), ax.get_ylim()[0]+(this_area_x+this_area_y)*((ax.get_ylim()[1]-ax.get_ylim()[0])/15),'Slope: '+str(format(slope, '.6f'))+' Intercept: '+str(format(inter, '.3f')), fontsize=15, color=colors[color_tmp], bbox=bbox_props)
                    color_tmp = color_tmp+1
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            plt.xlabel('Exposure time [us]') 
            plt.ylabel('Mean[DN]') 
            plt.savefig(figure_dir+"sensitivity_fit.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
            plt.savefig(figure_dir+"sensitivity_fit.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
                              
        #open report file
        report_file = figure_dir+"Report_results_APS"+".txt"
        out_file = open(report_file,"w")  
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                out_file.write("\n")
                out_file.write("X: " + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y])+"\n")           
                if(ptc_dir.lower().find('dark') >= 0):
                    out_file.write("Dark current is: " + str(format(i_pd_es[this_area_y,this_area_x], '.4f')) + " e/s or " + str(i_pd_vs[this_area_y,this_area_x])  + " v/s or " + str(i_pd_es[this_area_y,this_area_x]*1.6*10**(-19))+ " A\n")
                else:
                    out_file.write("Photodiode current is: " + str(format(i_pd_es[this_area_y,this_area_x], '.4f')) + " e/s or " + str(i_pd_vs[this_area_y,this_area_x])  + " v/s or " + str(i_pd_es[this_area_y,this_area_x]*1.6*10**(-19))+ " A\n")
        out_file.close()
        if(ptc_dir.lower().find('dark') < 0):
            return i_pd_vs, Gain_uVe_lin
        else:
            return i_pd_vs