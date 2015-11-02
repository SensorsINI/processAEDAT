###############################
# # plot frame images obtained
# # from net_raw_UDP_jAER
# # federico.corradi@inilabs.com
###############################

import pylab as plt
from time import sleep

def display_APS_frames(frames, time_interval=1):
    '''
    display DAVIS240 frames with fixed time interval
    inputs:
        frames : obtained from net_raw_UDP_jAER.py
        time_interval : optional parameter, time interval in between frames
    '''
    plt.ion()
    my_obj = plt.imshow(plt.rot90(frames[1][3, :, :]))
    plt.hold('on')
    for i in range(len(frames)):
        frames[i][3, :, :] = frames[i][2, :, :] - frames[i][1, :, :]
        frames[i][6, :, :] = frames[i][5, :, :] - frames[i][4, :, :]
        frames[i][3, :, :][frames[i][3, :, :] < 0] = 0
        my_obj.set_data(plt.rot90(frames[i][3, :, :]))
        plt.draw()
        sleep(1)
