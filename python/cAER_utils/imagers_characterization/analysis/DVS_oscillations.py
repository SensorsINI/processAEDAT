# ############################################################
# python class that deals with cAER aedat3 file format
# and calculates OSCILLATIONS of DVS
# author  Federico Corradi - federico.corradi@inilabs.com
# author  Diederik Paul Moeys - diederikmoeys@live.com
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


class DVS_oscillations:
    def __init__(self):
        self.loader = load_files.load_files()
        self.V3 = "aedat3"
        self.V2 = "aedat"  # current 32bit file format
        self.V1 = "dat"  # old format
        self.header_length = 28
        self.EVT_DVS = 0  # DVS event type
        self.EVT_APS = 2  # APS event
        self.file = []
        self.x_addr = []
        self.y_addr = []
        self.timestamp = []
        self.time_res = 1e-6

    def oscillations_latency_analysis(self, latency_pixel_dir, figure_dir, camera_dim=[190, 180], size_led=2,
                                      confidence_level=0.75, do_plot=True, file_type="cAER", edges=2, dvs128xml=False,
                                      pixel_sel=False, latency_only=False):
        '''
            oscillations/latency, single pixel signal reconstruction
            ----
            paramenters:
                 latency_pixel_dir  -> measurements directory
                 figure_dir         -> figure directory *where to store the figures*
        '''
        import string as stra
        import matplotlib.pyplot as plt
        #################################################################
        ############### OSCILLATIONS ANALISYS
        #################################################################
        # get all files in dir
        directory = latency_pixel_dir
        # files_in_dir = os.listdir(directory)
        # files_in_dir.sort()
        files_in_dir = [f for f in os.listdir(directory) if not f.startswith('.')]  # no hidden file
        files_in_dir.sort()

        all_latencies_mean_up = []
        all_latencies_mean_dn = []

        all_latencies_std_up = []
        all_latencies_std_dn = []

        # loop over all recordings
        all_lux = []
        all_filters_type = []

        all_prvalues = []
        all_valuesPos = []
        all_valuesNeg = []
        all_bins = []
        all_originals = []
        all_folded = []
        all_ts = []
        all_pol = []
        all_xaddr = []
        all_yaddr = []
        all_final_index = []

        for this_file in range(len(files_in_dir)):
            # exp_settings = string.split(files_in_dir[this_file],"_")
            # exp_settings_bias_fine = string.split(exp_settings[10], ".")[0]
            # exp_settings_bias_coarse = exp_settings[8]

            print("Processing file " + str(this_file + 1) + " of " + str(len(files_in_dir)))

            if not os.path.isdir(directory + files_in_dir[this_file]):
                if (file_type == "cAER"):
                    [frame, xaddr, yaddr, pol, ts, sp_type, sp_t] = self.loader.load_file(
                        directory + files_in_dir[this_file])
                    current_lux = stra.split(files_in_dir[this_file], "_")[8]
                    filter_type = stra.split(files_in_dir[this_file], "_")[10]
                    all_lux.append(current_lux)
                    all_filters_type.append(filter_type)
                    try:
                        all_prvalues.append(int(stra.split(files_in_dir[this_file], '_')[12]))
                    except IndexError:
                        all_prvalues = [1]
            else:
                print("Skipping path " + str(directory + files_in_dir[this_file]) + " as it is a directory")
                continue

            if do_plot:
                fig = plt.figure()
                plt.subplot(4, 1, 1)
                dx = plt.hist(xaddr, camera_dim[0])
                dy = plt.hist(yaddr, camera_dim[1])
            if (pixel_sel == False):
                ind_x_max = int(st.mode(xaddr)[
                                    0])  # int(np.floor(np.median(xaddr)))#np.where(dx[0] == np.max(dx[0]))[0]#CB# 194
                ind_y_max = int(
                    st.mode(yaddr)[0])  # int(np.floor(np.median(yaddr)))#np.where(dy[0] == np.max(dy[0]))[0]#CB#45
                print("selected pixel x: " + str(ind_x_max))
                print("selected pixel y: " + str(ind_y_max))
            else:
                print("using pixels selected from user x,y: " + str(pixel_sel))
                ind_x_max = pixel_sel[0]
                ind_y_max = pixel_sel[1]

            # if(len(ind_x_max) > 1):
            #    ind_x_max = np.floor(np.mean(ind_x_max))
            # if(len(ind_y_max) > 1):
            #    ind_y_max = np.floor(np.mean(ind_y_max))

            ts = np.array(ts)
            pol = np.array(pol)
            xaddr = np.array(xaddr)
            yaddr = np.array(yaddr)
            sp_t = np.array(sp_t)
            sp_type = np.array(sp_type)
            pixel_box = size_led * 2 + 1
            pixel_num = pixel_box ** 2

            x_to_get = np.linspace(ind_x_max - size_led, ind_x_max + size_led, pixel_box)
            y_to_get = np.linspace(ind_y_max - size_led, ind_y_max + size_led, pixel_box)

            index_to_get, un = self.ismember(xaddr, x_to_get)
            indey_to_get, un = self.ismember(yaddr, y_to_get)
            final_index = (index_to_get & indey_to_get)

            if (dvs128xml == False):
                index_up_jump = sp_type == 2
                index_dn_jump = sp_type == 3
            else:  # DVS128 only detects one edge
                # we only have a single edge
                index_up_jump = sp_type == 2
                index_dn_jump = sp_type == 2
                # we assume 50% duty cicle and we add the second edge
                sp_t_n = []
                sp_type_n = []
                period_diff = np.mean(np.diff(sp_t))
                for i in range(len(sp_t)):
                    sp_t_n.append(sp_t[i])
                    sp_t_n.append(sp_t[i] + int(period_diff / 2.0))
                    sp_type_n.append(sp_type[i])
                    sp_type_n.append(3)  ##add transition
                sp_type_n = np.array(sp_type_n)
                sp_t_n = np.array(sp_t_n)
                sp_t = sp_t_n
                sp_type = sp_type_n

            original = np.zeros(len(ts))
            this_index = 0
            for i in range(len(ts)):  # label all events with the high or low of the square wave
                if (ts[i] < sp_t[this_index]):
                    original[i] = sp_type[this_index]
                elif (ts[i] >= sp_t[this_index]):
                    original[i] = sp_type[this_index]
                    if (this_index != len(sp_t) - 1):
                        this_index = this_index + 1

            stim_freq = np.mean(1.0 / (np.diff(sp_t) * self.time_res * 2))
            print("stimulus frequency was :" + str(stim_freq))

            if (not latency_only):
                delta_up = np.ones(camera_dim)
                delta_dn = np.ones(camera_dim)
                delta_up_count = np.zeros(camera_dim)
                delta_dn_count = np.zeros(camera_dim)

                for x_ in range(np.min(xaddr[final_index]), np.max(xaddr[final_index])):
                    for y_ in range(np.min(yaddr[final_index]), np.max(yaddr[final_index])):
                        this_index_x = xaddr[final_index] == x_
                        this_index_y = yaddr[final_index] == y_
                        index_to_get = this_index_x & this_index_y
                        delta_up_count[x_, y_] = np.sum(pol[final_index][index_to_get] == 1)
                        delta_dn_count[x_, y_] = np.sum(pol[final_index][index_to_get] == 0)

                counter_x = 0
                counter_tot = 0
                latency_up_tot = []
                latency_dn_tot = []
                signal_rec = []
                ts_t = []
                for x_ in range(np.min(xaddr[final_index]), np.max(xaddr[final_index])):
                    counter_y = 0
                    for y_ in range(np.min(yaddr[final_index]), np.max(yaddr[final_index])):
                        tmp_rec = []
                        tmp_t = []
                        this_index_x = xaddr[final_index] == x_
                        this_index_y = yaddr[final_index] == y_
                        index_to_get = this_index_x & this_index_y
                        # get the balance between up and down delta
                        if (delta_up_count[x_, y_] > delta_dn_count[x_, y_]):
                            delta_dn[x_, y_] = (delta_up_count[x_, y_] / np.double(delta_dn_count[x_, y_])) * (
                                delta_up[x_, y_])
                        else:
                            delta_up[x_, y_] = (delta_dn_count[x_, y_] / np.double(delta_up_count[x_, y_])) * (
                                delta_dn[x_, y_])

                        tmp = 0
                        counter_transitions_up = 0
                        counter_transitions_dn = 0
                        for this_ev in range(np.sum(index_to_get)):
                            if (pol[final_index][index_to_get][this_ev] == 1):
                                tmp_rec.append(tmp)
                                tmp_t.append(ts[final_index][index_to_get][this_ev] - 1)

                                tmp = tmp + delta_up[x_, y_]
                                tmp_rec.append(tmp)
                                tmp_t.append(ts[final_index][index_to_get][this_ev])
                                # get first up transition for this pixel
                                if (counter_transitions_up < len(sp_t[index_up_jump])):
                                    if (sp_t[index_up_jump][counter_transitions_up] < ts[final_index][index_to_get][
                                        this_ev]):
                                        this_latency = ts[final_index][index_to_get][this_ev] - sp_t[index_up_jump][
                                            counter_transitions_up]
                                        this_neuron = [xaddr[final_index][index_to_get][this_ev],
                                                       yaddr[final_index][index_to_get][this_ev]]
                                        if (this_latency > 0):
                                            latency_up_tot.append([this_latency, this_neuron])
                                            counter_transitions_up = counter_transitions_up + 1  # as soon as one on event is seen, move on to next sync edge
                            if (pol[final_index][index_to_get][this_ev] == 0):
                                tmp_rec.append(tmp)
                                tmp_t.append(ts[final_index][index_to_get][this_ev] - 1)

                                tmp = tmp - delta_dn[x_, y_]
                                tmp_rec.append(tmp)
                                tmp_t.append(ts[final_index][index_to_get][this_ev])
                                if (counter_transitions_dn < len(sp_t[index_dn_jump])):
                                    if (sp_t[index_dn_jump][counter_transitions_dn] < ts[final_index][index_to_get][
                                        this_ev]):
                                        this_latency = ts[final_index][index_to_get][this_ev] - sp_t[index_dn_jump][
                                            counter_transitions_dn]
                                        this_neuron = [xaddr[final_index][index_to_get][this_ev],
                                                       yaddr[final_index][index_to_get][this_ev]]
                                        if (this_latency > 0):
                                            latency_dn_tot.append([this_latency, this_neuron])
                                            counter_transitions_dn = counter_transitions_dn + 1

                        signal_rec.append(tmp_rec)
                        ts_t.append(tmp_t)

                # open report file
                report_file = figure_dir + "Report_results_" + str(this_file) + ".txt"
                out_file = open(report_file, "w")
                out_file.write("lux: " + str(current_lux) + " filter type" + str(filter_type) + "\n")
                if (len(latency_up_tot) > 0):
                    latencies_up = []
                    for i in range(1, len(latency_up_tot) - 1):
                        tmp = latency_up_tot[i][0]
                        latencies_up.append(tmp)
                    latencies_up = np.array(latencies_up)
                    all_latencies_mean_up.append(np.mean(latencies_up))
                    err_up = self.confIntMean(latencies_up, conf=confidence_level)
                    all_latencies_std_up.append(err_up)
                    print("mean latency up: " + str(np.mean(latencies_up)) + " us")
                    out_file.write("mean latency up: " + str(np.mean(latencies_up)) + " us\n")
                    print("err latency up: " + str(err_up) + " us")
                    out_file.write("err latency up: " + str(err_up) + " us\n")

                if (len(latency_dn_tot) > 0):
                    latencies_dn = []
                    for i in range(1, len(latency_dn_tot) - 1):
                        tmp = latency_dn_tot[i][0]
                        latencies_dn.append(tmp)
                    latencies_dn = np.array(latencies_dn)
                    all_latencies_mean_dn.append(np.mean(latencies_dn))
                    err_dn = self.confIntMean(latencies_dn, conf=confidence_level)
                    all_latencies_std_dn.append(err_dn)
                    print("mean latency dn: " + str(np.mean(latencies_dn)) + " us")
                    out_file.write("mean latency dn: " + str(np.mean(latencies_dn)) + " us\n")
                    print("err latency dn: " + str(err_dn) + " us")
                    out_file.write("err latency dn: " + str(err_dn) + " us\n")
                out_file.close()
                signal_rec = np.array(signal_rec)
                original = original - np.mean(original)
                amplitude_rec = np.abs(np.max(original)) + np.abs(np.min(original))
                original = original / amplitude_rec
                all_originals.append(original)

            # folding all cycles into one for histogram
            # ts_changes = np.where(np.diff(original) != 0)
            # ts_folds = sp_t[index_up_jump]
            # fold ts
            # ts_folded = []
            # counter_fold = 0
            # for this_ts in range(len(ts)):
            #    for this_fold in range(len(ts_folds) - 1):
            #        if(ts[this_ts] >= ts_folds[this_fold] and ts[this_ts] < ts_folds[this_fold + 1]):
            #            ts_folded.append(ts[this_ts] - ts_folds[this_fold])

            # ts_folded = np.array(ts_folded)
            # all_folded.append(ts_folded)

            all_pol.append(pol)
            all_xaddr.append(xaddr)
            all_yaddr.append(yaddr)
            all_final_index.append(final_index)
            all_ts.append(ts)

            if do_plot:

                plt.subplot(4, 1, 2)
                plt.plot(ts[final_index], pol[final_index] * 0.5, "o", color='blue')

                plt.plot(ts, original * 2, "x--", color='red')
                plt.subplot(4, 1, 3)
                plt.plot((ts - np.min(ts)), original, linewidth=3)
                plt.xlim([0, np.max(ts) - np.min(ts)])
                if (not latency_only):
                    for i in range(len(signal_rec)):
                        if (len(signal_rec[i]) > 2):
                            signal_rec[i] = signal_rec[i] - np.mean(signal_rec[i])
                            amplitude_rec = np.abs(np.max(signal_rec[i])) + np.abs(np.min(signal_rec[i]))
                            norm = signal_rec[i] / amplitude_rec
                            plt.plot((np.array(ts_t[i]) - np.min(ts[i])), norm, '-')
                        else:
                            print("skipping neuron")

                ax = fig.add_subplot(4, 1, 4, projection='3d')
                x = xaddr
                y = yaddr
                histo, xedges, yedges = np.histogram2d(x, y, bins=(20, 20))  # =(np.max(yaddr),np.max(xaddr)))
                xpos, ypos = np.meshgrid(xedges[:-1] + xedges[1:], yedges[:-1] + yedges[1:])
                xpos = xpos.flatten() / 2.
                ypos = ypos.flatten() / 2.
                zpos = np.zeros_like(xpos)
                dx = xedges[1] - xedges[0]
                dy = yedges[1] - yedges[0]
                dz = histo.flatten()
                ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='r', zsort='average')
                plt.xlabel("X")
                plt.ylabel("Y")
                # Find maximum point
                plt.savefig(figure_dir + "combined_latency_" + str(this_file) + ".png", format='png', dpi=300)

        if (dvs128xml == False):
            if do_plot:
                all_lux = np.array(all_lux)
                all_filters_type = np.array(all_filters_type)
                all_latencies_mean_up = np.array(all_latencies_mean_up)
                all_latencies_mean_dn = np.array(all_latencies_mean_dn)
                all_latencies_std_up = np.array(all_latencies_std_up)
                all_latencies_std_dn = np.array(all_latencies_std_dn)

                if (len(all_latencies_mean_up) > 0):
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    plt.title("final latency plots with filter: " + str(all_filters_type[0]))
                    plt.errorbar(np.array(all_lux, dtype=float) / np.power(10, np.double(all_filters_type[0])),
                                 all_latencies_mean_up, yerr=all_latencies_mean_up - all_latencies_std_up.T[0],
                                 markersize=4, marker='o', label='UP')
                    plt.errorbar(np.array(all_lux, dtype=float) / np.power(10, np.double(all_filters_type[0])),
                                 all_latencies_mean_dn, yerr=all_latencies_mean_dn - all_latencies_std_dn.T[0],
                                 markersize=4, marker='o', label='DN')
                    ax.set_xscale("log", nonposx='clip')
                    ax.set_yscale("log", nonposx='clip')
                    ax.grid(True, which="both", ls="--")
                    plt.xlabel('lux')
                    plt.ylabel('latency [us]')
                    plt.legend(loc='best')
                    plt.savefig(figure_dir + "all_latencies_" + str(this_file) + ".pdf", format='PDF')
                    plt.savefig(figure_dir + "all_latencies_" + str(this_file) + ".png", format='PNG')

                all_lux = np.array(all_lux)
                all_prvalues = np.array(all_prvalues)
                all_ts = np.array(all_ts)
                all_originals = np.array(all_originals)
                all_folded = np.array(all_folded)
                all_pol = np.array(all_pol)
                all_xaddr = np.array(all_xaddr)
                all_yaddr = np.array(all_yaddr)

                # just plot 2x2 center pixels
                edges = 2
                import matplotlib.pyplot as plt
                import pylab
                nb_values = len(np.unique(all_prvalues))
                nl_values = len(np.unique(all_lux))
                if (nl_values == 1 and nb_values == 1):
                    nl_values += 1
                    nb_values += 1
                f, axarr = plt.subplots(nl_values, nb_values)
                for this_file in range(len(all_ts)):
                    current_ts = all_ts[this_file][all_final_index[this_file]]
                    current_pol = all_pol[this_file][all_final_index[this_file]]
                    current_xaddr = all_xaddr[this_file][all_final_index[this_file]]
                    current_yaddr = all_yaddr[this_file][all_final_index[this_file]]
                    #current_ts_original = all_ts[this_file]
                    #current_original = all_originals[this_file]

                    # now fold signal
                    ts_folds = sp_t[index_dn_jump]  # one every two edges
                    ts_subtract = 0
                    ts_folded = []
                    pol_folded = []
                    spike_order_folded = []
                    counter_fold = 0
                    this_fold = 0
                    start_saving = False
                    on_spike_count = np.zeros([len(x_to_get), len(y_to_get)])
                    off_spike_count = np.zeros([len(x_to_get), len(y_to_get)])
                    for this_ts in range(len(current_ts)):
                        if ((current_ts[this_ts] >= ts_folds[this_fold + 1]) and (
                                    this_fold < len(ts_folds) - 2)):
                            # raise Exception
                            this_fold = this_fold + 1
                            on_spike_count = np.zeros([len(x_to_get), len(y_to_get)])
                            off_spike_count = np.zeros([len(x_to_get), len(y_to_get)])
                            print "Moving to fold # " + str(this_fold)
                        if (current_ts[this_ts] >= ts_folds[this_fold] and current_ts[this_ts] < ts_folds[
                                this_fold + 1]):
                            ts_folded.append(current_ts[this_ts] - ts_folds[this_fold])
                            pol_folded.append(current_pol[this_ts])
                            if (current_pol[this_ts] == 1):
                                on_spike_count[
                                    current_xaddr[this_ts] - x_to_get[0], current_yaddr[this_ts] - y_to_get[0]] = \
                                    on_spike_count[
                                        current_xaddr[this_ts] - x_to_get[0], current_yaddr[this_ts] - y_to_get[0]] + 1
                                spike_order_folded.append(on_spike_count[
                                                              current_xaddr[this_ts] - x_to_get[0], current_yaddr[
                                                                  this_ts] - y_to_get[0]])
                            elif (current_pol[this_ts] == 0):
                                off_spike_count[
                                    current_xaddr[this_ts] - x_to_get[0], current_yaddr[this_ts] - y_to_get[0]] = \
                                    off_spike_count[
                                        current_xaddr[this_ts] - x_to_get[0], current_yaddr[this_ts] - y_to_get[0]] + 1
                                spike_order_folded.append(off_spike_count[
                                                              current_xaddr[this_ts] - x_to_get[0], current_yaddr[
                                                                  this_ts] - y_to_get[0]])

                    # for this_ts in range(len(current_ts)):
                    #    if(counter_fold < len(ts_folds)):
                    #        if(current_ts[this_ts] >= ts_folds[counter_fold]):
                    #            ts_subtract = ts_folds[counter_fold]
                    #            counter_fold += 1
                    #            start_saving = True
                    #    if(start_saving):
                    #        ts_folded.append(current_ts[this_ts] - ts_subtract)
                    #        pol_folded.append(current_pol[this_ts])
                    ts_folded = np.array(ts_folded)
                    pol_folded = np.array(pol_folded)
                    spike_order_folded = np.array(spike_order_folded)
                    # raise Exception
                    meanPeriod = np.mean(ts_folds[1::] - ts_folds[0:-1:])  # / 2.0
                    binss = np.linspace(0, meanPeriod, 1000)
                    # starting = len(current_ts)-len(ts_folded)
                    dn_index = np.logical_and(pol_folded == 0, spike_order_folded == 1)
                    up_index = np.logical_and(pol_folded == 1, spike_order_folded == 1)
                    valuesPos = np.histogram(ts_folded[up_index], bins=binss)
                    valuesNeg = np.histogram(ts_folded[dn_index], bins=binss)
                    # raise Exception
                    latency_off_hist_peak = binss[np.argmax(valuesNeg[0])]
                    rising_edge = np.mean(sp_t[index_up_jump] - sp_t[index_dn_jump])
                    latency_on_hist_peak = binss[np.argmax(valuesPos[0])] - rising_edge
                    print ("On latency from histogram peak: " + str(latency_on_hist_peak) + " us")
                    print ("Off latency from histogram peak: " + str(latency_off_hist_peak) + " us")
                    latency_off_folded_mean = np.mean(ts_folded[dn_index])
                    latency_on_folded_mean = np.mean(ts_folded[up_index]) - rising_edge
                    print ("On latency from folded mean: " + str(latency_on_folded_mean) + " us")
                    print ("Off latency from folded mean: " + str(latency_off_folded_mean) + " us")

                    # plot in the 2d grid space of biases vs lux
                    n_lux = []
                    for i in range(len(all_lux)):
                        n_lux.append(int(float(all_lux[i])))
                    n_lux = np.array(n_lux)
                    n_pr = []
                    for i in range(len(all_prvalues)):
                        n_pr.append(int(float(all_prvalues[i])))
                    n_pr = np.array(n_pr)
                    rows = int(np.where(n_lux[this_file] == np.unique(n_lux))[0])
                    cols = int(np.where(n_pr[this_file] == np.unique(n_pr))[0])
                    axarr[rows, cols].bar(binss[1::], valuesPos[0], width=10, color="g")
                    axarr[rows, cols].bar(binss[1::], 0 - valuesNeg[0], width=10, color="r")
                    axarr[rows, cols].plot([rising_edge, rising_edge], [-np.max(valuesNeg[0]), np.max(valuesPos[0])])
                    axarr[rows, cols].text(np.max(binss[1::]) / 4.0, -25,
                                           'lux = ' + str(all_lux[this_file]) + '\n' + 'PrBias = ' + str(
                                               all_prvalues[this_file]) + '\n', fontsize=11, color='b')
                    plt.savefig(figure_dir + "all_latencies_hist" + str(this_file) + ".pdf", format='PDF')
                    plt.savefig(figure_dir + "all_latencies_hist" + str(this_file) + ".png", format='PNG')

        return all_lux, all_prvalues, all_originals, all_folded, all_pol, all_ts, all_final_index

    def confIntMean(self, a, conf=0.95):
        mean, sem, m = np.mean(a), st.sem(a), st.t.ppf((1 + conf) / 2., len(a) - 1)
        return mean - m * sem, mean + m * sem

    def rms(self, predictions, targets):
        return np.sqrt(np.mean((predictions - targets) ** 2))

    def ismember(self, a, b):
        '''
        as matlab: ismember
        '''
        # tf = np.in1d(a,b) # for newer versions of numpy
        tf = np.array([i in b for i in a])
        u = np.unique(a[tf])
        index = np.array([(np.where(b == i))[0][-1] if t else 0 for i, t in zip(a, tf)])
        return tf, index

    # log(sine) wave to fit
    def my_log_sin(self, x, freq, amplitude, phase, offset_in, offset_out):
        return np.log(-np.sin(2 * np.pi * x * freq + phase) * amplitude + offset_in) + offset_out
