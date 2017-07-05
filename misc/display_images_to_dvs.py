# author federico.corradi@inilabs.com
# pick images from a folder and display them on the screen
# to simulate micro-saccadic movement, it shakes the images at about 10hz

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
from os import listdir
from os.path import isfile, join
import time

pause = False
start = time.time() 
n_seconds = 10
this_image = 0

directory = '/home/federico/iniLabs/3rdparty/opencv/opencv-3.0.0/train_classifier/positive_images_norm_crop_display/' 
onlyfiles = [ f for f in listdir(directory) if isfile(join(directory,f)) ]
onlyfiles.sort()

plt.ion()

data = []
for i in range(len(onlyfiles)):
    data.append(np.asarray(Image.open(directory+onlyfiles[i]).convert('L')))

fig = plt.figure()

im = plt.imshow(data[1], cmap=plt.get_cmap('Greys_r'), interpolation='nearest')


def onClick(event):
    global pause
    if(pause == False):
        pause ^= True
    if(pause == True):
        pause ^= False    

def image_select():
    global start
    global n_seconds
    global this_image
    timer = time.time()
    #print "timer", timer
    #print "start", start
    #print "n_seconds", n_seconds
    if ( (timer-start) >= (n_seconds)):
        #print "timer+start", timer+start
        #print "start+n_seconds", start+n_seconds
        this_image = this_image+1
        start = timer

#fig.canvas.mpl_connect('button_press_event', onClick)
    
def updatefig(*args):
    global data
    global pause
    global this_image
    image_select()
    if not pause:
        #print m.tolist()
        data_t = np.roll(data[this_image],-int(np.random.normal(0)*5+10), axis=1)
        data_t = np.roll(data_t,int(np.random.normal(0)*4), axis=0)
        im.set_array(data_t)
        return im,
    return im,

ani = animation.FuncAnimation(fig, updatefig, interval=90, blit=True, repeat=True)
#plt.show()
