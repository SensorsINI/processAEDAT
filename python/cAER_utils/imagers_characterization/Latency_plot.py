# -*- coding: utf-8 -*-
"""
Created on Fri Aug 05 16:19:34 2016

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
lux = [1,10,100,1000,1500]
ON_latency = [2590,105,55,35,25] #us
OFF_latency = [960,55,44,10,30] #us

lux2 = [10,100,1000]
ON_latency1 = [455,110,15] #us
OFF_latency1 = [670,115,20] #us

fig=plt.figure()
colors = cm.rainbow(np.linspace(0, 1, 4))
color_tmp = 0
ax = fig.add_subplot(111)
plt.loglog(lux, OFF_latency, 'o--', color=colors[color_tmp], label='sDAVIS OFF')
color_tmp = color_tmp+1
plt.loglog(lux, ON_latency, 'o--', color=colors[color_tmp], label='sDAVIS ON')
color_tmp = color_tmp+1
plt.loglog(lux2, OFF_latency1, 'o--', color=colors[color_tmp], label='DAVIS240C OFF')
color_tmp = color_tmp+1
plt.loglog(lux2, ON_latency1, 'o--', color=colors[color_tmp], label='DAVIS240C ON')
plt.xlabel("Illuminance [lux]")
plt.ylabel("Latency [us]")
ax.set_title('ON and OFF latencies vs illuminance')
lgd = plt.legend(loc=1)
plt.xlim((0.99,1700))
plt.ylim((5,3000))
fig.tight_layout() 
plt.savefig(folder+"latency_vs_lux.pdf",  format='PDF', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.savefig(folder+"latency_vs_lux.png",  format='PNG', bbox_extra_artists=(lgd,), bbox_inches='tight', dpi=dpinum)
plt.close("all")