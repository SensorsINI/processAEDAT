# -*- coding: utf-8 -*-
"""
Created on Tue Aug 02 20:53:28 2016

@author: Diederik Paul Moeys
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from pylab import *
sys.path.append('utils/')
import operator
import matplotlib.ticker as ticker


folder = "C:/Users/Diederik Paul Moeys/Desktop/"
dpinum = 1000
lux = [30,60,600]
lux_no_dvs = [0.1,30,60,600]
if dvs:
    a18_pow = np.zeros([len(lux),len(activity)])
    a33_pow = np.zeros([len(lux),len(activity)])
    d18_pow = np.zeros([len(lux),len(activity)])
    d33_pow = np.zeros([len(lux),len(activity)])
else:
    a18_pow = np.zeros([len(lux_no_dvs),len(activity)])
    a33_pow = np.zeros([len(lux_no_dvs),len(activity)])
    d18_pow = np.zeros([len(lux_no_dvs),len(activity)])
    d33_pow = np.zeros([len(lux_no_dvs),len(activity)])
low_power = True
dvs = False

if dvs:
    activity = [100,1000,2000] #keps
    if low_power:
        a18_pow[0,:] = [x * 1.8 for x in [5.20, 5.00, 4.50]] #mW
        a33_pow[0,:] = [x * 3.3 for x in [0, 0, 0]] #mW disconnected
        d18_pow[0,:] = [x * 1.8 for x in [0.11, 0.15, 0.20]] #mW
        d33_pow[0,:] = [x * 3.3 for x in [0.52, 0.66, 2.2]] #mW
        a18_pow[1,:] = [x * 1.8 for x in [7.40, 7.10, 6.9]] #mW
        a33_pow[1,:] = [x * 3.3 for x in [0, 0, 0]] #mW
        d18_pow[1,:] = [x * 1.8 for x in [0.10, 0.12, 0.22]] #mW
        d33_pow[1,:] = [x * 3.3 for x in [0.60, 1.2, 2.4]] #mW
        a18_pow[2,:] = [x * 1.8 for x in [11.90, 10.5, 10.5]] #mW
        a33_pow[2,:] = [x * 3.3 for x in [3.2, 3.2, 3.2]] #mW
        d18_pow[2,:] = [x * 1.8 for x in [0.02, 0.1, 0.19]] #mW
        d33_pow[2,:] = [x * 3.3 for x in [0.47, 1.5, 2.4]] #mW
        a18_pow_no_dvs = [x * 1.8 for x in [2.70, 4.90, 5.20, 2.70]] #mW
        a33_pow_no_dvs = [x * 3.3 for x in [0.43, 0, 0, 3.1]] #mW
        d18_pow_no_dvs = [x * 1.8 for x in [0, 0, 0, 0]] #mW
        d33_pow_no_dvs = [x * 3.3 for x in [0.95, 0.95, 0.95, 0.95]] #mW
    else:
        a18_pow[0,:] = [x * 1.8 for x in [24, 24, 24]] #mW
        a33_pow[0,:] = [x * 3.3 for x in [3.10, 3.10, 3.10]] #mW
        d18_pow[0,:] = [x * 1.8 for x in [0.10, 0.12, 0.22]] #mW
        d33_pow[0,:] = [x * 3.3 for x in [0.50, 1, 2]] #mW
        a18_pow[1,:] = [x * 1.8 for x in [24.60, 24.60, 24.60]] #mW
        a33_pow[1,:] = [x * 3.3 for x in [3.20, 3.20, 3.20]] #mW
        d18_pow[1,:] = [x * 1.8 for x in [0.10, 0.12, 0.22]] #mW
        d33_pow[1,:] = [x * 3.3 for x in [0.50, 1, 2]] #mW
        a18_pow[2,:] = [x * 1.8 for x in [27, 27.6, 27.6]] #mW
        a33_pow[2,:] = [x * 3.3 for x in [3.2, 3.2, 3.2]] #mW
        d18_pow[2,:] = [x * 1.8 for x in [0.10, 0.12, 0.22]] #mW
        d33_pow[2,:] = [x * 3.3 for x in [0.50, 1, 2]] #mW
        a18_pow_no_dvs = [x * 1.8 for x in [0.4, 4.4, 6, 11.30]] #mW
        a33_pow_no_dvs = [x * 3.3 for x in [2.7, 2.7, 2.7, 2.7]] #mW
        d18_pow_no_dvs = [x * 1.8 for x in [0.95, 0.95, 0.95, 0.95]] #mW
        d33_pow_no_dvs = [x * 3.3 for x in [0.95, 0.95, 0.95, 0.95]] #mW
else:
    activity = [1,10,30] #frames
    lux = lux_no_dvs
    if low_power:
        a18_pow[0,:] = [x * 1.8 for x in [17, 17, 17]] #mW
        a33_pow[0,:] = [x * 3.3 for x in [7.8, 7.8, 7.8]] #mW
        d18_pow[0,:] = [x * 1.8 for x in [0.07, 0.07, 0.07]] #mW
        d33_pow[0,:] = [x * 3.3 for x in [0.9, 0.9, 2.5]] #mW
        a18_pow[1,:] = [x * 1.8 for x in [17, 17, 17]] #mW
        a33_pow[1,:] = [x * 3.3 for x in [7.4, 7.4, 7.5]] #mW
        d18_pow[1,:] = [x * 1.8 for x in [0.07, 0.07, 0.07]] #mW
        d33_pow[1,:] = [x * 3.3 for x in [0.9, 0.9, 2.5]] #mW
        a18_pow[2,:] = [x * 1.8 for x in [17, 17, 17]] #mW
        a33_pow[2,:] = [x * 3.3 for x in [7.2, 7.4, 7.5]] #mW
        d18_pow[2,:] = [x * 1.8 for x in [0.07, 0.07, 0.07]] #mW
        d33_pow[2,:] = [x * 3.3 for x in [0.9, 0.9, 2.5]] #mW
        a18_pow[3,:] = [x * 1.8 for x in [17, 17, 17]] #mW
        a33_pow[3,:] = [x * 3.3 for x in [6.9, 7.4, 7.5]] #mW
        d18_pow[3,:] = [x * 1.8 for x in [0.07, 0.07, 0.07]] #mW
        d33_pow[3,:] = [x * 3.3 for x in [0.9, 0.9, 2.5]] #mW
        a18_pow_no_dvs = [x * 1.8 for x in [16.4, 16.4, 16.4, 16.4]] #mW
        a33_pow_no_dvs = [x * 3.3 for x in [2.7, 2.7, 2.7, 2.7]] #mW
        d18_pow_no_dvs = [x * 1.8 for x in [0.05, 0.05, 0.05, 0.05]] #mW
        d33_pow_no_dvs = [x * 3.3 for x in [0.95, 0.95, 0.95, 0.95]] #mW
    else:
        a18_pow[0,:] = [x * 1.8 for x in [3.9, 3.9, 3.9]] #mW
        a33_pow[0,:] = [x * 3.3 for x in [10, 10, 10]] #mW
        d18_pow[0,:] = [x * 1.8 for x in [0.07, 0.07, 0.07]] #mW
        d33_pow[0,:] = [x * 3.3 for x in [0.9, 0.9, 0.9]] #mW
        a18_pow[1,:] = [x * 1.8 for x in [7.4, 7.4, 7.4]] #mW
        a33_pow[1,:] = [x * 3.3 for x in [10, 10, 10]] #mW
        d18_pow[1,:] = [x * 1.8 for x in [0.07, 0.07, 0.07]] #mW
        d33_pow[1,:] = [x * 3.3 for x in [0.9, 0.9, 0.9]] #mW
        a18_pow[2,:] = [x * 1.8 for x in [8, 8, 8]] #mW
        a33_pow[2,:] = [x * 3.3 for x in [10, 10, 10]] #mW
        d18_pow[2,:] = [x * 1.8 for x in [0.07, 0.07, 0.07]] #mW
        d33_pow[2,:] = [x * 3.3 for x in [0.9, 0.9, 0.9]] #mW
        a18_pow[3,:] = [x * 1.8 for x in [14, 14, 14]] #mW
        a33_pow[3,:] = [x * 3.3 for x in [10, 10, 10]] #mW
        d18_pow[3,:] = [x * 1.8 for x in [0.07, 0.07, 0.07]] #mW
        d33_pow[3,:] = [x * 3.3 for x in [0.9, 0.9, 0.9]] #mW
        a18_pow_no_dvs = [x * 1.8 for x in [0.4, 4.4, 6, 11.30]] #mW
        a33_pow_no_dvs = [x * 3.3 for x in [2.7, 2.7, 2.7, 2.7]] #mW
        d18_pow_no_dvs = [x * 1.8 for x in [0.05, 0.05, 0.05, 0.05]] #mW
        d33_pow_no_dvs = [x * 3.3 for x in [0.95, 0.95, 0.95, 0.95]] #mW
    
overall_pow = a18_pow + a33_pow + d18_pow + d33_pow
overall_pow_no_dvs = np.sum([a18_pow_no_dvs, a33_pow_no_dvs, d18_pow_no_dvs, d33_pow_no_dvs],axis= 0)

#POWER vs ACTIVITY
fig=plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 5))
for this_activity in range(len(activity)):
   color_tmp = 0
   ax = fig.add_subplot(1,3,this_activity+1)
   plt.plot(lux, a18_pow[:,this_activity], '^-', color=colors[color_tmp], label='A1.8')
   color_tmp = color_tmp+1
   plt.plot(lux, a33_pow[:,this_activity], 's-', color=colors[color_tmp], label='A3.3')
   color_tmp = color_tmp+1
   plt.plot(lux, d18_pow[:,this_activity], 'd-', color=colors[color_tmp], label='D1.8')
   color_tmp = color_tmp+1
   plt.plot(lux, d33_pow[:,this_activity], 'o-', color=colors[color_tmp], label='D3.3')
   color_tmp = color_tmp+1
   plt.plot(lux, overall_pow[:,this_activity], '*--', color=colors[color_tmp], label='Overall')
   color_tmp = color_tmp+1
   plt.xlabel("Illuminance [lux]")
   plt.ylabel("Power consumption [mW]")
   if dvs:
       ax.set_title(str(activity[this_activity]) + ' keps')
   else:
       ax.set_title(str(activity[this_activity]) + ' fps')
   plt.ylim((0,np.max(overall_pow)+1))   
   start, end = ax.get_xlim()
   step = 200
   ax.xaxis.set_ticks(np.arange(start, end+step, step))
   ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
   plt.show()
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.tight_layout() 
if dvs:
    if low_power:
        plt.savefig(folder+"power_vs_lux_low_dvs.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_lux_low_dvs.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
    else:
        plt.savefig(folder+"power_vs_lux_high_dvs.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_lux_high_dvs.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
else:
    if low_power:
        plt.savefig(folder+"power_vs_lux_low_aps.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_lux_low_aps.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
    else:
        plt.savefig(folder+"power_vs_lux_high_aps.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_lux_high_aps.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
plt.close("all")

#POWER vs LUX
fig=plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 5))
for this_lux in range(len(lux)):
   color_tmp = 0
   ax = fig.add_subplot(1,len(lux),this_lux+1)
   if dvs:
       plt.semilogx(activity, a18_pow[this_lux,:], '^-', color=colors[color_tmp], label='A1.8')
       color_tmp = color_tmp+1
       plt.semilogx(activity, a33_pow[this_lux,:], 's-', color=colors[color_tmp], label='A3.3')
       color_tmp = color_tmp+1
       plt.semilogx(activity, d18_pow[this_lux,:], 'd-', color=colors[color_tmp], label='D1.8')
       color_tmp = color_tmp+1
       plt.semilogx(activity, d33_pow[this_lux,:], 'o-', color=colors[color_tmp], label='D3.3')
       color_tmp = color_tmp+1
       plt.semilogx(activity, overall_pow[this_lux,:], '*--', color=colors[color_tmp], label='Overall')
       color_tmp = color_tmp+1
       plt.xlabel("Activity [keps]")
       plt.xlim((50,4000))
       plt.ylim((0,np.max(overall_pow)+1))
   else:
       plt.plot(activity, a18_pow[this_lux,:], '^-', color=colors[color_tmp], label='A1.8')
       color_tmp = color_tmp+1
       plt.plot(activity, a33_pow[this_lux,:], 's-', color=colors[color_tmp], label='A3.3')
       color_tmp = color_tmp+1
       plt.plot(activity, d18_pow[this_lux,:], 'd-', color=colors[color_tmp], label='D1.8')
       color_tmp = color_tmp+1
       plt.plot(activity, d33_pow[this_lux,:], 'o-', color=colors[color_tmp], label='D3.3')
       color_tmp = color_tmp+1
       plt.plot(activity, overall_pow[this_lux,:], '*--', color=colors[color_tmp], label='Overall')
       color_tmp = color_tmp+1
       plt.xlabel("Frames [fps]")
       plt.ylim((0,np.max(overall_pow)+1)) 
       start, end = ax.get_xlim()
       step = 10
       ax.xaxis.set_ticks(np.arange(start, end+step, step))
       plt.show()
   plt.ylabel("Power consumption [mW]")
   ax.set_title(str(lux[this_lux]) + ' lux')
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.tight_layout()
if dvs: 
    if low_power:
        plt.savefig(folder+"power_vs_act_low_dvs.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_act_low_dvs.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
    else:
        plt.savefig(folder+"power_vs_act_high_dvs.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_act_high_dvs.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
else:
    if low_power:
        plt.savefig(folder+"power_vs_fra_low_aps.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_fra_low_aps.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
    else:
        plt.savefig(folder+"power_vs_fra_high_aps.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_fra_high_aps.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)   
plt.close("all")

#POWER vs LUX for no DVS and APS
fig=plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 5))
color_tmp = 0
ax = fig.add_subplot(111)
plt.plot(lux_no_dvs, a18_pow_no_dvs, '^-', color=colors[color_tmp], label='A1.8')
color_tmp = color_tmp+1
plt.plot(lux_no_dvs, a33_pow_no_dvs, 's-', color=colors[color_tmp], label='A3.3')
color_tmp = color_tmp+1
plt.plot(lux_no_dvs, d18_pow_no_dvs, 'd-', color=colors[color_tmp], label='D1.8')
color_tmp = color_tmp+1
plt.plot(lux_no_dvs, d33_pow_no_dvs, 'o-', color=colors[color_tmp], label='D3.3')
color_tmp = color_tmp+1
plt.plot(lux_no_dvs, overall_pow_no_dvs, '*--', color=colors[color_tmp], label='Overall')
color_tmp = color_tmp+1
plt.ylim((0,np.max(overall_pow_no_dvs)+1))   
start, end = ax.get_xlim()
step = 200
ax.xaxis.set_ticks(np.arange(start, end+step, step))
ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
plt.show()
plt.xlabel("Illuminance [lux]")
plt.ylabel("Power consumption [mW]")
ax.set_title('Static power consumption')
lgd = plt.legend(loc=2)
fig.tight_layout() 
if dvs:
    if low_power:
        plt.savefig(folder+"power_vs_lux_no_dvs_low_dvs.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_lux_no_dvs_low_dvs.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
    else:
        plt.savefig(folder+"power_vs_lux_no_dvs_high_dvs.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_lux_no_dvs_high_dvs.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)  
else:
    if low_power:
        plt.savefig(folder+"power_vs_lux_no_aps_low_aps.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_lux_no_aps_low_aps.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
    else:
        plt.savefig(folder+"power_vs_lux_no_aps_high_aps.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.savefig(folder+"power_vs_lux_no_aps_high_aps.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)  

plt.close("all")