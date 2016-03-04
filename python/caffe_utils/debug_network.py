#!/usr/bin/env python
"""
Authors: federico.corradi@inilabs.com, diederikmoeys@live.com

Test Caffe Network

"""
import numpy as np
import re
from matplotlib import pylab as plt
import numpy as np
import os
import sys
import argparse
import glob
import time
import pandas as pd
from PIL import Image
import scipy
import caffe
import re
from caffe.proto import caffe_pb2
from google.protobuf import text_format
import pydot
import base64
import struct

prototxt_net = "lenet.prototxt"
weight_files = "newdb_lenet_15000_spikes_iter__iter_538000.caffemodel"

this_classifier = caffe.Classifier(prototxt_net,weight_files)

#im_f = glob.glob('/home/ubuntu/caffe/data/facedetection_36x36/pos_train_lfw_9917.png')
#inputs =[caffe.io.load_image(im_f[0], False)]

#plt.imshow(np.reshape(inputs,[36,36]))
#plt.savefig("tmp.png")

fake_img = np.ones([36,36])

for x in range(36):
    for y in range(36):
        fake_img[x,y] = (x+y)/(36.0+36.0)


fake_img = np.fliplr(np.flipud(np.rot90(fake_img)))
inputs = np.reshape(fake_img, [1,36,36,1])

plt.figure()
plt.imshow(fake_img, interpolation="nearest", cmap='gray')
plt.colorbar()
plt.savefig("tmps/input_.png")

predictions = this_classifier.predict(inputs)

filters = this_classifier.params['conv1'][0].data
num_f, dim, kx, ky = np.shape(filters)
for this_dim in range(dim):
    plt.figure()
    for this_f in range(num_f):
       plt.subplot(num_f, 1, this_f+1)
       frame = plt.gca()
       frame.axes.get_xaxis().set_visible(False)
       frame.axes.get_yaxis().set_visible(False)
       plt.imshow(filters[this_f,this_dim,:,:], interpolation="nearest", cmap="gray",origin='lower')
plt.savefig("tmps/filters1_.png")

nkernel, inputfeaturesmaps, kx, ky = np.shape(this_classifier.params['conv2'][0].data)
feat = this_classifier.params['conv2'][0].data
num_f, dim, kx, ky = np.shape(feat)
counter_i = 1
plt.figure()
for this_dim in range(nkernel):
    for this_f in range(inputfeaturesmaps):
        plt.subplot(inputfeaturesmaps, nkernel, counter_i)
        frame = plt.gca()
        plt.title("o"+str(this_dim)+" i"+str(this_f))
        plt.imshow(feat[this_dim,this_f,:,:], interpolation="nearest", cmap="gray", origin='lower')
        counter_i = counter_i +1
        frame.axes.get_xaxis().set_visible(False)
        frame.axes.get_yaxis().set_visible(False)
plt.savefig("tmps/filters2_.png")

un, nkernel, kx, ky = np.shape(this_classifier.blobs['conv1'].data)
for i in range(nkernel):
    this_map = np.reshape(this_classifier.blobs['conv1'].data[0,i,:,:],[kx,ky])
    print("CONV 1 MAP NUMBER "+str(i))
    print(this_map)	
    plt.figure()
    plt.imshow(this_map, interpolation="nearest", cmap='gray')#,  origin='lower')
    plt.colorbar()
    plt.savefig("tmps/conv1_out_"+str(i)+".png")

un, nkernel, kx, ky = np.shape(this_classifier.blobs['conv2'].data)
for i in range(nkernel):
    this_map = np.reshape(this_classifier.blobs['conv2'].data[0,i,:,:],[kx,ky])
    print("CONV 2 MAP NUMBER "+str(i))
    print(this_map)
    plt.figure()
    plt.imshow(this_map, interpolation="nearest", cmap='gray')#,  origin='lower')
    plt.colorbar()
    plt.savefig("tmps/conv2_out_"+str(i)+".png")

#actfix = []
#fully_connected_weights = this_classifier.params['ip1'][0].data
#cols, rows = np.shape(fully_connected_weights)
#nkernel, inputfeaturesmaps, kx, ky = np.shape(this_classifier.params['conv2'][0].data)
#featurespixels = rows/nkernel #### ROWS
#featureside = np.sqrt(featurespixels)                     
#act=np.arange(featurespixels) 
#counter_i = 1
#plt.figure()
#for i in range(nkernel):
#    for j in range(cols):
#        plt.subplot(nkernel, cols, counter_i)
#        frame = plt.gca()
#        plt.title("o"+str(j)+" i"+str(i))
#        fully_connected_weights = np.reshape(fully_connected_weights, [cols,rows])
#        act = fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] 
#        actback = np.reshape(act, (featureside,featureside)) 
#        print("FULLY CONNECTED 1 OUTPUT NEURON: " +str(j)+" MAP NUMBER "+str(i))
#        print(actback)
#        plt.imshow((np.flipud((actback))), interpolation="nearest", cmap='gray',  origin='lower')
#        counter_i = counter_i +1
#        frame.axes.get_xaxis().set_visible(False)
#        frame.axes.get_yaxis().set_visible(False)
#plt.savefig("tmps/fully_connected_.png")

#plt.close('all')
print("FULLY CONNECTED ACTIVATIONS")
print np.reshape(this_classifier.blobs['ip1'].data[1,:], len(this_classifier.blobs['ip1'].data[1,:]))
print np.reshape(this_classifier.blobs['ip2'].data[1,:], len(this_classifier.blobs['ip2'].data[1,:]))
print predictions
