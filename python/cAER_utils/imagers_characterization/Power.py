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
dpinum = 100
lux = [30,60,600]
activity = [100,1000,2000] #keps
a18_pow = np.zeros([len(lux),len(activity)])
a33_pow = np.zeros([len(lux),len(activity)])
d18_pow = np.zeros([len(lux),len(activity)])
d33_pow = np.zeros([len(lux),len(activity)])

a18_pow[0,:] = [x * 1.8 for x in [5.20, 5.00, 4.50]] #mW
a33_pow[0,:] = [x * 3.3 for x in [0, 0, 0]] #mW
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

overall_pow = a18_pow + a33_pow + d18_pow + d33_pow

lux_no_dvs = [0.1,30,60,600]
a18_pow_no_dvs = [x * 1.8 for x in [2.70, 4.90, 5.20, 2.70]] #mW
a33_pow_no_dvs = [x * 3.3 for x in [0.43, 0, 0, 3.1]] #mW
d18_pow_no_dvs = [x * 1.8 for x in [0, 0, 0, 0]] #mW
d33_pow_no_dvs = [x * 3.3 for x in [0.95, 0.95, 0.95, 0.95]] #mW
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
   ax.set_title(str(activity[this_activity]) + ' keps')
   plt.ylim((0,np.max(overall_pow)+1))   
   start, end = ax.get_xlim()
   step = 200
   ax.xaxis.set_ticks(np.arange(start, end+step, step))
   ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
   plt.show()
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.tight_layout() 
plt.savefig(folder+"power_vs_lux.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(folder+"power_vs_lux.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
plt.close("all")

#POWER vs LUX
fig=plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 5))
for this_lux in range(len(lux)):
   color_tmp = 0
   ax = fig.add_subplot(1,3,this_lux+1)
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
   plt.ylabel("Power consumption [mW]")
   ax.set_title(str(lux[this_lux]) + ' lux')
   plt.ylim((0,np.max(overall_pow)+1))
   plt.xlim((50,4000))
lgd = plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
fig.tight_layout() 
plt.savefig(folder+"power_vs_act.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(folder+"power_vs_act.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
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
ax.set_title('Power consumption for DVS and APS turned off')
lgd = plt.legend(loc=2)
fig.tight_layout() 
plt.savefig(folder+"power_vs_lux_no_dvs.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(folder+"power_vs_lux_no_dvs.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
plt.close("all")