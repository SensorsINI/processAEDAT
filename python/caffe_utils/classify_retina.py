#!/usr/bin/env python
"""
Author: federico.corradi@inilabs.com

 Deep Learning Interface with caffe, this script loads images and it classify them with caffe
	http://caffe.berkeleyvision.org/
"""
import numpy as np
import os
import sys
import argparse
import glob
import time
import pandas as pd
from PIL import Image

import caffe


caffe.set_mode_gpu()

pycaffe_dir = os.path.dirname('/home/ubuntu/caffe/')
image_dir = pycaffe_dir + '/examples/images/retina/'
net = 'mnist';#'bvlc_reference_caffenet';

## parameters
if net == 'bvlc_reference_caffenet':
    model="models/bvlc_reference_caffenet/deploy.prototxt"
    trained_weights="models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel"
    class_labels_file =  'data/ilsvrc12/synset_words.txt'
    image_dim=[256,256]
    mean_file='python/caffe/imagenet/ilsvrc_2012_mean.npy'
    type_f = float
    default_f = 255.0
    default_swap = '2,1,0'   #BGR 
    default_ext = 'png'
    #load label classes
    with open(class_labels_file) as f:
        labels_df = pd.DataFrame([
                    {
                        'synset_id': l.strip().split(' ')[0],
                        'name': ' '.join(l.strip().split(' ')[1:]).split(',')[0]
                    }
                    for l in f.readlines()
                ])
    labels = labels_df.sort('synset_id')['name'].values

    #image_dims = [int(s) for s in args.images_dim.split(',')]
    mean = np.load(mean_file)

    # Make classifier.
    classifier = caffe.Classifier(model, trained_weights,
             image_dims=image_dim, mean=mean.mean(1).mean(1),
            input_scale=255.0,raw_scale=255.0)

if net == 'mnist':
    model="examples/mnist/lenet.prototxt"
    trained_weights="examples/mnist/lenet_iter_10000.caffemodel"
    image_dim=[28,28]
    classifier = caffe.Classifier(model, trained_weights, image_dims=(256, 256), raw_scale=255)


while(1):
    files_to_classify = os.listdir(image_dir)
    files_to_classify.sort()


    if(len(files_to_classify) > 2):
        files_to_classify = files_to_classify[0:len(files_to_classify)-1]

        try:
            inputs = [caffe.io.load_image(image_dir+files_to_classify[0], color=False)]
            os.remove(image_dir+files_to_classify[0])
        except IOError:
            #print("skipping image")
            continue
        except ValueError:
            continue

        print("Classifying %d inputs." % len(inputs))

        # Classify.
        start = time.time()
        scores = classifier.predict(inputs, oversample=True).flatten()
        indices = (-scores).argsort()[:5]

        if net == 'bvlc_reference_caffenet':
            predictions = labels[indices]
            meta = [
                        (p, '%.5f' % scores[i])
                        for i, p in zip(indices, predictions)
                    ]
            print("#CLASSIFICATION RESULTS")
            print(meta)

        if(net == 'mnist'):
            print("NUMBER:" + str( np.where(scores == np.max(scores))[0]) )    
            print("confidence :" +str(scores[indices][0]))


