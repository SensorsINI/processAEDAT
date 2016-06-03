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
import struct
import threading
import sys
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import string
from pylab import *
import scipy.stats as st
import math
sys.path.append('utils/')
import load_files

class APS_photon_transfer_curve:
    def ptc_analysis(self, sensor, ptc_dir, frame_y_divisions, frame_x_divisions, ADC_range, ADC_values):
        '''
            Photon transfer curve and sensitivity plot
         
        '''    
        figure_dir = ptc_dir+'/figures/'
        if(not os.path.exists(figure_dir)):
            os.makedirs(figure_dir)
        #pixel_area = (18e-6*18e-6)
        exposure_time_scale = 10e-6
        directory = ptc_dir
        files_in_dir = os.listdir(directory)
        files_in_dir.sort()
        u_y_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
        sigma_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])+1*-1
        std_tot = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        exposures = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        FPN_all = np.zeros([len(files_in_dir),len(frame_y_divisions),len(frame_x_divisions)])
        u_y_mean_frames = []
        all_frames = []
        done = False
        for this_file in range(len(files_in_dir)):
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
                    #avr_all_frames = []
                    #for this_frame in range(n_frames):
                    #    avr_all_frames.append(np.mean(frame_areas[this_frame]))
                    #avr_all_frames = np.array(avr_all_frames)       
                    #u_y = (1.0/(n_frames*ydim*xdim)) * np.sum(np.sum(frame_areas,0))  # 
                    xdim_f , ydim_f = np.shape(frame_areas[0])
                    temporal_mean = np.zeros([xdim_f, ydim_f])
                    temporal_variance = np.zeros([xdim_f, ydim_f])
                    #temporal_variance_EMVA = 0
                    #factor = (1.0/(2.0*float(xdim_f*ydim_f)))
                    for tx in range(xdim_f):
                        for ty in range(ydim_f):
                            temporal_mean[tx,ty] = np.mean(frame_areas[:,tx,ty])
                            temporal_variance[tx,ty] =  np.sum((frame_areas[:,tx,ty]-temporal_mean[tx,ty])**2)/n_frames
                            #temporal_variance_EMVA = temporal_variance_EMVA + (frame_areas[10,tx,ty]- frame_areas[11,tx,ty])**2.0
                    #temporal_variance_EMVA = factor*temporal_variance_EMVA
                    sigma_y = np.mean(temporal_variance)
                    #sigma_y = temporal_variance_EMVA
                    spatio_temporal_mean = np.mean(np.mean(temporal_mean,0),0)
                    spatio_var_temporal_mean = 0.0
                    for tx in range(xdim_f):
                        for ty in range(ydim_f):
                            spatio_var_temporal_mean = spatio_var_temporal_mean + (temporal_mean[tx,ty] - spatio_temporal_mean)**2.0
                    spatio_var_temporal_mean = spatio_var_temporal_mean / (xdim_f * ydim_f)
                    FPN = spatio_var_temporal_mean**0.5
                    #raise Exception                    
                    print("FPN: " + str(FPN) + "DN")
                    print("Temporal var: " + str(sigma_y) + "DN")
                    print(str(n_frames) + " frames recorded.")
#                    print(str(np.shape(all_frames)) + " all_frames.")
                    u_y_tot[this_file, this_div_y, this_div_x] = spatio_temporal_mean
                    sigma_tot[this_file, this_div_y, this_div_x] = sigma_y
                    exposures[this_file, this_div_y, this_div_x] = exp
                    FPN_all[this_file, this_div_y, this_div_x] = FPN
                    #u_y_mean_frames.append(spatio_temporal_mean) #average DN over time
        
        #just remove entry that corresponds to files that are not measurements
        files_num, y_div, x_div = np.shape(exposures)
        to_remove = len(np.unique(np.where(exposures == 0)[0]))
        exposures_real = exposures[exposures != 0]
        exposures = np.reshape(exposures_real, [files_num-to_remove, y_div, x_div])
        u_y_tot_real = u_y_tot[u_y_tot != -1]
        u_y_tot =  np.reshape(u_y_tot_real, [files_num-to_remove, y_div, x_div])
        sigma_tot_real = sigma_tot[sigma_tot != -1]
        sigma_tot =  np.reshape(sigma_tot_real, [files_num-to_remove, y_div, x_div])   
        exposures = exposures[:,0]
        #all_frames = np.array(all_frames)
        #plt.figure()
        #plt.title("all frames values")
        #for i in range(len(all_frames)):
        #    this_ff = np.reshape(all_frames[i], len(all_frames[i]))
        #    this_dn_f = np.right_shift(this_ff,6)
        #    plot(this_dn_f) 
        #plt.xlabel("frame number")   
        #plt.legend(loc='best')
        #plt.xlabel('frame number') 
        #plt.ylabel('DN value single pixel') 
        #plt.savefig(figure_dir+"dn_value_single_pixel.pdf",  format='pdf') 
        #plt.savefig(figure_dir+"dn_value_single_pixel.png",  format='png')  
    
        # sensitivity plot 
        plt.figure()
        plt.title("Sensitivity APS")
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                plt.plot( exposures[:,0], u_y_tot[:,this_area_y,this_area_x], 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
                color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel('exposure time [us]') 
        plt.ylabel('Mean[DN]') 
        plt.savefig(figure_dir+"sensitivity.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
        plt.savefig(figure_dir+"sensitivity.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
    
        # photon transfer curve 
        plt.figure()
        plt.title("Photon Transfer Curve")
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                plt.plot( u_y_tot[:,this_area_y,this_area_x] , sigma_tot[:,this_area_y,this_area_x] , 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
                color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.xlabel('Mean[DN] ') 
        plt.ylabel('Var[DN^2] ')
        plt.savefig(figure_dir+"ptc.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
        plt.savefig(figure_dir+"ptc.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        # photon transfer curve log 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.title("Photon Transfer Curve")
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                #raise Exception
                plt.plot( u_y_tot[:,this_area_y,this_area_x]-u_y_tot[0,this_area_y,this_area_x] , np.sqrt(sigma_tot[:,this_area_y,this_area_x]), 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) )
                color_tmp = color_tmp+1
        lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        ax.set_xscale("log", nonposx='clip')
        ax.set_yscale("log", nonposy='clip')
        plt.xlabel('Mean[DN] ') 
        plt.ylabel('STD[DN] ')
        plt.savefig(figure_dir+"log_ptc.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
        plt.savefig(figure_dir+"log_ptc.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)

        print("Log fit...")
        slope_tot = []
        inter_tot = []
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        un, y_div, x_div = np.shape(u_y_tot)
        colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
        color_tmp = 0;
        for this_area_x in range(x_div):
            for this_area_y in range(y_div):
                sigma_fit = sigma_tot[1:-1,this_area_y, this_area_x]
                max_var = np.max(sigma_fit)
                max_ind_var = np.where(sigma_fit  == max_var)[0][0]
                this_mean_values = u_y_tot[1:-1,this_area_y, this_area_x]-u_y_tot[0,this_area_y,this_area_x]
                this_mean_values_lin = this_mean_values[0:max_ind_var]
                try: 
                    #raise Exception
                    slope, inter = np.polyfit(log(this_mean_values_lin.reshape(len(this_mean_values_lin))),log(np.sqrt(sigma_fit.reshape(len(sigma_fit))[0:max_ind_var])),1)
                    failed = False
                except ValueError:
                    print("Poly Fit Failed for this recording.. skipping")
                    failed = True
                    continue
                #print("slope: "+str(slope))
                Gain_uVe = -inter/slope;
                print("Conversion gain: "+str(format(Gain_uVe, '.2f'))+"uV/e for X: " + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]))
                fit_fn = np.poly1d([slope, inter]) 
                ax.plot( log(u_y_tot[:,this_area_y, this_area_x]-u_y_tot[0,this_area_y,this_area_x]), log(np.sqrt(sigma_tot[:,this_area_y, this_area_x])), 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) +' with conversion gain: '+ str(format(Gain_uVe, '.2f')) + ' uV/e')
                ax.plot(log(this_mean_values_lin.reshape(len(this_mean_values_lin))), fit_fn(log(this_mean_values_lin.reshape(len(this_mean_values_lin)))), '-*', markersize=4, color=colors[color_tmp])
                bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=2)
                color_tmp = color_tmp+1
        color_tmp = 0;
        if(failed == False):
            for this_area_x in range(len(frame_x_divisions)):
                for this_area_y in range(len(frame_y_divisions)):
                    ax.text( ax.get_xlim()[1]+((ax.get_xlim()[1]-ax.get_xlim()[0])/10), ax.get_ylim()[0]+(this_area_x+this_area_y)*((ax.get_ylim()[1]-ax.get_ylim()[0])/15),'Slope:'+str(format(slope, '.3f'))+' Intercept:'+str(format(inter, '.3f')), fontsize=15, color=colors[color_tmp], bbox=bbox_props)
                    color_tmp = color_tmp+1
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)  
            plt.xlabel('log(Mean[DN])') 
            plt.ylabel('log(STD[DN])')
            plt.savefig(figure_dir+"ptc_log_fit.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
            plt.savefig(figure_dir+"ptc_log_fit.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)
        
            print("Linear fit...")
            slope_tot = []
            inter_tot = []
            fig = plt.figure()
            ax = fig.add_subplot(111)
            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            un, y_div, x_div = np.shape(u_y_tot)
            colors = cm.rainbow(np.linspace(0, 1, x_div*y_div))
            color_tmp = 0;
            for this_area_x in range(x_div):
                for this_area_y in range(y_div):
                    sigma_fit = sigma_tot[:,this_area_y, this_area_x]
                    max_var = np.max(sigma_fit)
                    max_ind_var = np.where(sigma_fit  == max_var)[0][0]
                    this_mean_values = u_y_tot[:,this_area_y, this_area_x]
                    this_mean_values_lin = this_mean_values[0:max_ind_var]
                    slope, inter = np.polyfit(this_mean_values_lin.reshape(len(this_mean_values_lin)), sigma_fit.reshape(len(sigma_fit))[0:max_ind_var],1)
                    Gain_uVe = ((ADC_range*slope)/ADC_values)*1000000;
                    print("Conversion gain: "+str(format(Gain_uVe, '.2f'))+"uV/e for X: " + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]))
                    fit_fn = np.poly1d([slope, inter]) 
                    ax.plot( u_y_tot[:,this_area_y, this_area_x], sigma_tot[:,this_area_y, this_area_x], 'o--', color=colors[color_tmp], label='X: ' + str(frame_x_divisions[this_area_x]) + ', Y: ' + str(frame_y_divisions[this_area_y]) +' with conversion gain: '+ str(format(Gain_uVe, '.2f')) + ' uV/e')
                    ax.plot(this_mean_values_lin.reshape(len(this_mean_values_lin)), fit_fn(this_mean_values_lin.reshape(len(this_mean_values_lin))), '-*', markersize=4, color=colors[color_tmp])
                    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=2)
                    color_tmp = color_tmp+1
            color_tmp = 0;
            for this_area_x in range(len(frame_x_divisions)):
                for this_area_y in range(len(frame_y_divisions)):
                    ax.text( ax.get_xlim()[1]+((ax.get_xlim()[1]-ax.get_xlim()[0])/10), ax.get_ylim()[0]+(this_area_x+this_area_y)*((ax.get_ylim()[1]-ax.get_ylim()[0])/15),'Slope:'+str(format(slope, '.3f'))+' Intercept:'+str(format(inter, '.3f')), fontsize=15, color=colors[color_tmp], bbox=bbox_props)
                    color_tmp = color_tmp+1
            lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)  
            plt.xlabel('Mean[DN]') 
            plt.ylabel('Var[DN^2]')
            plt.savefig(figure_dir+"ptc_linear_fit.pdf",  format='pdf', bbox_extra_artists=(lgd,), bbox_inches='tight') 
            plt.savefig(figure_dir+"ptc_linear_fit.png",  format='png', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=1000)

        #open report file
        report_file = figure_dir+"Report_results_APS"+".txt"
        out_file = open(report_file,"w")
        #raise Exception
        for this_file in range(len(exposures)):
            out_file.write("Exposure " +str(exposures[this_file,0]) + " us:\n")
            for this_area_x in range(x_div):
                for this_area_y in range(y_div):
                    out_file.write("Division (x,y) " + str(this_area_x) + "," + str(this_area_y) + ":\n")
                    out_file.write("Spatiotemporal mean (DN): " + str(u_y_tot[this_file, this_area_y, this_area_x]) + "\n")
                    out_file.write("FPN (DN): " + str(FPN_all[this_file, this_area_y, this_area_x]) + "\n")
                    out_file.write("FPN (%): " + str(100.0*(FPN_all[this_file, this_area_y, this_area_x]/u_y_tot[this_file, this_area_y, this_area_x])) + "%\n")
                    out_file.write("Temporal variance (DN^2): " + str(sigma_tot[this_file, this_area_y, this_area_x]) + "\n")
                    out_file.write("Temporal SD (%): " + str(100.0*((sigma_tot[this_file, this_area_y, this_area_x]**0.5)/u_y_tot[this_file, this_area_y, this_area_x])) + "%\n")
        out_file.close()

    def confIntMean(self, a, conf=0.95):
        mean, sem, m = np.mean(a), st.sem(a), st.t.ppf((1+conf)/2., len(a)-1)
        return mean - m*sem, mean + m*sem

    def ismember(self, a, b):
        '''
        as matlab: ismember
        '''
        # tf = np.in1d(a,b) # for newer versions of numpy
        tf = np.array([i in b for i in a])
        u = np.unique(a[tf])
        index = np.array([(np.where(b == i))[0][-1] if t else 0 for i,t in zip(a,tf)])
        return tf, index
