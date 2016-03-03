#!/usr/bin/env python
"""
Authors: federico.corradi@inilabs.com, diederikmoeys@live.com

Converts caffe networks into jAER xml format

 this script requires command line arguments: 
                         model file -> network.prototxt  
                         weights file -> caffenet.model
                        OR
                         if you pass a directory it will look for these files

Example usage:
     python python/cnn_to_xml.py caffe_network_directory/ (it looks for .caffemodel and .prototxt)

"""
import numpy as np
import re
import click
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

def get_pooling_types_dict():
    """Get dictionary mapping pooling type number to type name
    """
    desc = caffe_pb2.PoolingParameter.PoolMethod.DESCRIPTOR
    d = {}
    for k, v in desc.values_by_name.items():
        d[v.number] = k
    return d


def get_edge_label(layer):
    """Define edge label based on layer type.
    """

    if layer.type == 'Data':
        edge_label = 'Batch ' + str(layer.data_param.batch_size)
    elif layer.type == 'Convolution' or layer.type == 'Deconvolution':
        edge_label = str(layer.convolution_param.num_output)
    elif layer.type == 'InnerProduct':
        edge_label = str(layer.inner_product_param.num_output)
    else:
        edge_label = '""'

    return edge_label


def get_layer_label(layer, rankdir):
    """Define node label based on layer type.

    Parameters
    ----------
    layer : ?
    rankdir : {'LR', 'TB', 'BT'}
        Direction of graph layout.

    Returns
    -------
    string :
        A label for the current layer
    """

    if rankdir in ('TB', 'BT'):
        # If graph orientation is vertical, horizontal space is free and
        # vertical space is not; separate words with spaces
        separator = ' '
    else:
        # If graph orientation is horizontal, vertical space is free and
        # horizontal space is not; separate words with newlines
        separator = '\\n'

    if layer.type == 'Convolution' or layer.type == 'Deconvolution':
        # Outer double quotes needed or else colon characters don't parse
        # properly
        param = layer.convolution_param
        node_label = '"%s%s(%s)%skernel size: %d%sstride: %d%spad: %d"' %\
                    (layer.name,
                     separator,
                     layer.type,
                     separator,
                     layer.convolution_param.kernel_size[0] if len(layer.convolution_param.kernel_size._values) else 1,
                     separator,
                     layer.convolution_param.stride[0] if len(layer.convolution_param.stride._values) else 1,
                     separator,
                     layer.convolution_param.pad[0] if len(layer.convolution_param.pad._values) else 0)
    elif layer.type == 'Pooling':
        pooling_types_dict = get_pooling_types_dict()
        node_label = '"%s%s(%s %s)%skernel size: %d%sstride: %d%spad: %d"' %\
                     (layer.name,
                      separator,
                      pooling_types_dict[layer.pooling_param.pool],
                      layer.type,
                      separator,
                      layer.pooling_param.kernel_size,
                      separator,
                      layer.pooling_param.stride,
                      separator,
                      layer.pooling_param.pad)
    else:
        node_label = '"%s%s(%s)"' % (layer.name, separator, layer.type)
    return node_label

def get_pydot_graph(caffe_net, rankdir, label_edges=True):
    """Create a data structure which represents the `caffe_net`.
    Parameters
    ----------
    caffe_net : object
    rankdir : {'LR', 'TB', 'BT'}
        Direction of graph layout.
    label_edges : boolean, optional
        Label the edges (default is True).
    Returns
    -------
    pydot graph object
    """
    pydot_graph = pydot.Dot(caffe_net.name,
                            graph_type='digraph',
                            rankdir=rankdir)
    pydot_nodes = {}
    pydot_edges = []
    for layer in caffe_net.layer:
        node_label = get_layer_label(layer, rankdir)
        node_name = "%s_%s" % (layer.name, layer.type)
        if (len(layer.bottom) == 1 and len(layer.top) == 1 and
           layer.bottom[0] == layer.top[0]):
            # We have an in-place neuron layer.
            pydot_nodes[node_name] = pydot.Node(node_label,
                                                **NEURON_LAYER_STYLE)
        else:
            layer_style = LAYER_STYLE_DEFAULT
            layer_style['fillcolor'] = choose_color_by_layertype(layer.type)
            pydot_nodes[node_name] = pydot.Node(node_label, **layer_style)
        for bottom_blob in layer.bottom:
            pydot_nodes[bottom_blob + '_blob'] = pydot.Node('%s' % bottom_blob,
                                                            **BLOB_STYLE)
            edge_label = '""'
            pydot_edges.append({'src': bottom_blob + '_blob',
                                'dst': node_name,
                                'label': edge_label})
        for top_blob in layer.top:
            pydot_nodes[top_blob + '_blob'] = pydot.Node('%s' % (top_blob))
            if label_edges:
                edge_label = get_edge_label(layer)
            else:
                edge_label = '""'
            pydot_edges.append({'src': node_name,
                                'dst': top_blob + '_blob',
                                'label': edge_label})
    # Now, add the nodes and edges to the graph.
    for node in pydot_nodes.values():
        pydot_graph.add_node(node)
    for edge in pydot_edges:
        pydot_graph.add_edge(
            pydot.Edge(pydot_nodes[edge['src']],
                       pydot_nodes[edge['dst']],
                       label=edge['label']))
    return pydot_graph

@click.command()
@click.argument('dirs', nargs=-1, type=click.Path(exists=True, resolve_path=True))
def main(dirs):
    solvers = []
    classifiers = []
    nets = []
    net_files = [] 
    weight_files = []
    ip_present = False
    for i, log_dir in enumerate(dirs):
        print("working on >"+log_dir+"<"+str(i)+">")
        #find networks
        tmp_files = []
        for file in os.listdir(log_dir):
            if file.endswith("solver.prototxt"):
                #print("solver file >" +file)  
                solver = caffe_pb2.SolverParameter()
                prototxt_solver = log_dir +"/"+file
                #print("opening >" +prototxt_solver)
                f = open(prototxt_solver, 'r')
                text_format.Merge(str(f.read()), solver)            
                solvers.append(solver)
            if file.endswith(".prototxt") and not file.endswith("solver.prototxt") and not file.endswith("train_test.prototxt"):
                #print("net file >" +file)  
                net = caffe_pb2.NetParameter()
                prototxt_net = log_dir +"/"+file
                f = open(prototxt_net, 'r')
                text_format.Merge(f.read(), net)
                net_files.append(prototxt_net)
                nets.append(net)
            if file.endswith(".caffemodel"):
                #print("weight file >" +file)
                weight_net = log_dir +"/"+file
                tmp_files.append(weight_net)
        weight_files.append(tmp_files)
        # prototxt_net.prototxt, solver (net solver object)
        #find last weight snapshot for this net
        iter_num = -1 
        iter_index = 0
        for this_f in weight_files[0]:
            whole_path = str(this_f)
            cutted = whole_path.split(".caffemodel")
            #find num iterations
            #this assumes that before caffemodel we have filename accordingly to
            # _iternum.caffemodel
            #for this_c in cutted:
                #splitted = this_c.split("_")
                #try:
                    #this_iter = int(splitted[-1])
                    #if(int(this_iter) == solver.max_iter):
                    #    iter_num = iter_index 
                #except ValueError:              
                #    continue 
                #iter_index += 1
        print(prototxt_net)
        print(weight_files[0][iter_num])
        this_classifier = caffe.Classifier(prototxt_net,weight_files[0][iter_num])
        classifiers.append(this_classifier)

    nets_num = len(nets)    
    rankdir = "LR"
    #loop over all net in folder
    for this_net in range(nets_num):
        this_classifier = classifiers[this_net] #grub one net 
        nodes_label = []
        nodes_name  = []
        #header 
        net_string = '<?xml version="1.0" encoding="utf-8"?>\n'
        net_string += '<Network>\n'
        net_string += '<name>'+nets[this_net].name+'</name>\n'
        net_string += '<type>caffe_net</type>\n'
        net_string += '<notes>Built using cnn_to_xml.py Authors: federico.corradi@inilabs.com, diederikmoeys@live.com</notes>\n'
        net_string += '<nLayers>'+str(len(nets[this_net].layer))+'</nLayers>\n'
        net_string += '<dob>'+str(time.strftime("%d/%m/%Y %H:%M:%S"))+'</dob>\n'
        #input data layer
        bs, dim, x, y = nets[this_net].input_dim
        net_string += '\t<Layer>\n'
        net_string += '\t\t<index>0</index>\n'
        net_string += '\t\t<type>i</type>\n'
        net_string += '\t\t<dimx>'+str(x)+'</dimx>\n'
        net_string += '\t\t<dimy>'+str(y)+'</dimy>\n'
        net_string += '\t\t<nUnits>'+str(x*y*dim)+'</nUnits>\n'
        net_string += '\t</Layer>\n'
        inputmaps  = 1
        #initialize indices 
        count_lay = 1
        count_xml_layer = 0
        counter_ip_out = 1 
        layers_string = ''
        n_layer = len(nets[this_net].layer)
        #determines which one is the last output layer
        for layer in nets[this_net].layer:
            if(layer.type == 'InnerProduct'):
                output_layer_num = counter_ip_out
            counter_ip_out += 1 
        for layer in nets[this_net].layer:
            if( layer.type == 'Convolution' or layer.type == 'Pooling' or layer.type == 'InnerProduct'):
                net_string += '\t<Layer>\n'
            node_label = get_layer_label(layer, 'LR')
            node_name = "%s_%s" % (layer.name, layer.type)                    
            nodes_label.append(node_label)
            nodes_name.append(node_name)
            #find out what type of layer is this
            #  last layer is output layer by definition (this assumes that there is a Softmax or SoftmaxWithLoss
            #  layer at the very last in the prototxt network file)
            if(count_lay == output_layer_num):
                type_l = 'o'   
                count_xml_layer += 1 
            else:
                if(layer.type == 'Convolution'):
                    type_l = 'c'
                    count_xml_layer += 1
                elif(layer.type == 'Deconvolution'):
                    type_l = 'd'
                    count_xml_layer += 1
                elif(layer.type == 'Pooling'):
                    type_l = 's'    #danny calls it subsampling instead of pooling
                    count_xml_layer += 1
                elif(layer.type == 'InnerProduct'):
                    type_l = 'ip'
                    ip_present = True
                    count_xml_layer += 1
                else:
                    type_l = '"%s%s(%s)"' % (layer.name, "\\n", layer.type)
            #create xml entities
            if(type_l == 'c'):  #convolution
                outputmaps =  layer.convolution_param.num_output
                stride = layer.convolution_param.stride
                if (layer.convolution_param.kernel_size):
                    kernel_size = layer.convolution_param.kernel_size
                else:
                    kernel_size = 1
                this_kernels = this_classifier.params[layer.name][0].data
                this_biases = this_classifier.params[layer.name][1].data
                if(len(np.shape(this_biases)) > 3):
                    un1, un2, col_bi, row_bi = np.shape(this_biases)
                    this_biases_reshaped = np.reshape(this_biases, row_bi*col_bi)
                else:
                    row_bi = np.shape(this_biases)
                    this_biases_reshaped = np.reshape(this_biases, row_bi)
                s = " "
                this_biases = s.join(str(this_biases_reshaped[i]) for i in range(len(this_biases_reshaped)))
                nkernel, inputfeaturesmap, row_k, col_k = np.shape(this_kernels)
                re_arrenged_kernels = []
                counter = 0
                for i in range(inputfeaturesmap):
                    for k in range(nkernel):
                        this_kernels[k,i,:,:] = (np.flipud(np.rot90(this_kernels[k,i,:,:])))
                        re_arrenged_kernels.append(this_kernels[k,i,:,:].reshape(row_k*col_k))
                re_arrenged_kernels = np.array(re_arrenged_kernels)         
                final_k = []
                this_kernels_reshaped = np.reshape(np.transpose(re_arrenged_kernels), row_k*col_k*nkernel*inputfeaturesmap, order="F")
                this_kernels = s.join(str(this_kernels_reshaped[i]) for i in range(len(this_kernels_reshaped)))
                next_layer = nets[this_net].layer[count_lay]
                if ( next_layer.type == 'ReLU' ):
                    act_func = str.lower(str(next_layer.type))                                
                elif( next_layer.type == 'Sigmoid' ):
                    act_func = str.lower(str(next_layer.type))
                else:
                    act_func = 'none'      
                ### write XML 
                net_string += '\t\t<index>'+str(count_xml_layer)+'</index>\n'
                net_string += '\t\t<type>'+str(type_l)+'</type>\n'
                net_string += '\t\t<inputMaps>'+str(inputmaps)+'</inputMaps>\n'
                net_string += '\t\t<outputMaps>'+str(outputmaps)+'</outputMaps>\n'
                net_string += '\t\t<kernelSize>'+str(kernel_size[0])+'</kernelSize>\n'
                net_string += '\t\t<activationFunction>'+act_func+'</activationFunction>\n'
                net_string += '\t\t<biases dt="ASCII-float32">'+this_biases+'</biases>\n'
                net_string += '\t\t<kernels dt="ASCII-float32">'+this_kernels+'</kernels>\n'
                inputmaps = outputmaps
            elif(type_l == 'd'):  # deconvolution
                print("deconvolution not yet implemented.. skipping this layer")
            elif(type_l == 's'):  # pooling or subsampling
                #subsamplig = pooling
                this_biases = this_classifier.blobs[layer.name].data
                number1_bi, number2_bi, row_bi, col_bi = np.shape(this_biases)
                for i in range(number2_bi):
                    for k in range(number1_bi):
                        this_biases[k,i,:,:] = (np.flipud(np.rot90(this_biases[k,i,:,:])))
                this_biases_reshaped = np.reshape(this_biases, row_bi*col_bi*number1_bi*number2_bi)
                s = " "
                this_biases = s.join(str(this_biases_reshaped[i]) for i in range(len(this_biases_reshaped)))
                ### write XML 
                net_string += '\t\t<index>'+str(count_xml_layer)+'</index>\n'
                net_string += '\t\t<type>'+str(type_l)+'</type>\n'
                net_string += '\t\t<poolingType>'+str.lower(get_pooling_types_dict()[layer.pooling_param.pool])+'</poolingType>\n'
                net_string += '\t\t<averageOver dt="ASCII-float32">'+str(layer.pooling_param.kernel_size)+'</averageOver>\n'
                #net_string += '\t\t<biases dt="ASCII-float32">'+this_biases+'</biases>\n'
                net_string += '\t\t<strides>'+str(layer.pooling_param.stride)+'</strides>\n'
                net_string += '\t\t<pad>'+str(layer.pooling_param.pad)+'</pad>\n'   
            elif(type_l == 'ip' or type_l == 'o'): # fully connected or output
                next_layer = nets[this_net].layer[count_lay]
                if ( next_layer.type == 'ReLU' ):
                    act_func = str.lower(str(next_layer.type))                               
                elif( next_layer.type == 'Sigmoid' ):
                    act_func = str.lower(str(next_layer.type))
                else:
                    act_func = 'none'                         
                fully_connected_weights = this_classifier.params[layer.name][0].data
                if(len(np.shape(fully_connected_weights)) > 3):
                    if(type_l == 'ip'): 
                        un1, un2, cols, rows = np.shape(fully_connected_weights)
                        featurespixels = rows/outputmaps ### ROWS
                        featureside = np.sqrt(featurespixels)       
                        act=np.arange(featurespixels) 
                        for j in range(cols):
                            for i in range(outputmaps):
                                fully_connected_weights = np.reshape(fully_connected_weights, [cols,rows])
                                act = fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] 
                                actback = np.reshape(act, (featureside,featureside)) 
                                actfix = actback
                                fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] = np.reshape(actfix,  featurespixels, order="F") 
                        fully_connected_weights = np.transpose(fully_connected_weights) 
                        fully_connected_weights_reshaped = np.reshape(fully_connected_weights, rows*cols)
                    if(type_l == 'o'):
                        un1, un2, cols, rows = np.shape(fully_connected_weights)
                        featurespixels = cols/outputmaps #### COLS
                        featureside = np.sqrt(featurespixels)                     
                        act=np.arange(featurespixels) 
                        for j in range(cols):
                            for i in range(outputmaps):
                                fully_connected_weights = np.reshape(fully_connected_weights, [cols,rows])
                                act = fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] 
                                actback = np.reshape(act, (featureside,featureside)) 
                                actfix = (actback) 
                                fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] = np.reshape(actfix,  featurespixels)            
                        fully_connected_weights = np.transpose(fully_connected_weights) 
                        fully_connected_weights_reshaped = np.reshape(fully_connected_weights, rows*cols)
                else:
                    if(type_l == 'ip'): 
                        cols, rows = np.shape(fully_connected_weights)
                        featurespixels = rows/outputmaps ### ROWS
                        featureside = np.sqrt(featurespixels)       
                        act=np.arange(featurespixels) 
                        for j in range(cols):
                            for i in range(outputmaps):
                                fully_connected_weights = np.reshape(fully_connected_weights, [cols,rows])
                                act = fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] 
                                actback = np.reshape(act, (featureside,featureside)) 
                                actfix = actback
                                fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] = np.reshape(actfix,  featurespixels, order="F") 
                        fully_connected_weights = np.transpose(fully_connected_weights) 
                        fully_connected_weights_reshaped = np.reshape(fully_connected_weights, rows*cols)
                    if(type_l == 'o'):
                        cols, rows = np.shape(fully_connected_weights)
                        if(ip_present):
                            featurespixels = cols/outputmaps #### COLS
                        else:
                            featurespixels = rows/outputmaps #### ROWS
                        featureside = np.sqrt(featurespixels)                     
                        act=np.arange(featurespixels) 
                        for j in range(cols):
                            for i in range(outputmaps):
                                fully_connected_weights = np.reshape(fully_connected_weights, [cols,rows])
                                act = fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] 
                                actback = np.reshape(act, (featureside,featureside)) 
                                actfix = (actback) 
                                fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] = np.reshape(actfix,  featurespixels)            
                        fully_connected_weights = np.transpose(fully_connected_weights) 
                        fully_connected_weights_reshaped = np.reshape(fully_connected_weights, rows*cols)
                    
                biases_output = this_classifier.params[layer.name][1].data
                if(len(np.shape(biases_output)) > 3):
                    if(type_l == 'ip'):
                        un1, un2, cols_b, rows_b = np.shape(biases_output)
                        biases_output_reshaped = np.reshape(np.fliplr(np.flipud(np.rot90(biases_output))), un1*un2*cols_b*rows_b, order="F")
                    if(type_l == 'o'):
                        un1, un2, cols, rows = np.shape(biases_output)
                        featurespixels = cols/outputmaps
                        featureside = np.sqrt(featurespixels)          
                        act=np.arange(featurespixels) 
                        for j in range(cols):
                            for i in range(outputmaps):
                                fully_connected_weights = np.reshape(biases_output, [cols,rows])
                                act = fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] 
                                actback = np.reshape(act, (featureside,featureside)) 
                                actfix = (actback) 
                                fully_connected_weights[j,featurespixels*(i):featurespixels+featurespixels*(i)] = np.reshape(actfix,  featurespixels)                                
                        fully_connected_weights = (fully_connected_weights) 
                        biases_output_reshaped = np.reshape(fully_connected_weights, rows*cols)
                else:
                    rows_b = np.shape(biases_output)
                    biases_output_reshaped = np.reshape(biases_output, rows_b)
                s = " "
                biasweights = s.join(str(biases_output_reshaped[i]) for i in range(len(biases_output_reshaped)))       
                fully_connected_weights = s.join(str(fully_connected_weights_reshaped[i]) for i in range(len(fully_connected_weights_reshaped)))
                ### write XML 
                net_string += '\t\t<activationFunction>'+act_func+'</activationFunction>\n'
                net_string += '\t\t<index>'+str(count_xml_layer)+'</index>\n'
                net_string += '\t\t<type>'+str(type_l)+'</type>\n'
                net_string += '\t\t<biases dt="ASCII-float32">'+biasweights+'</biases>\n'
                net_string += '\t\t<weights cols="'+str(cols)+'" dt="ASCII-float32" rows="'+str(rows)+'">'+fully_connected_weights+'</weights>\n'
            if( layer.type == 'Convolution' or layer.type == 'Pooling' or layer.type == 'InnerProduct' ):   
                ### write XML 
                net_string += '\t</Layer>\n' #end layer
            count_lay += 1  
        net_string += '</Network>\n'
        #save xml to disc
        file_xml_name = net_files[this_net]+str('_jAER.xml')
        print("saving network in "+file_xml_name)
        with open(file_xml_name, "w") as text_file:
            text_file.write(net_string)


if __name__ == '__main__':
    main()