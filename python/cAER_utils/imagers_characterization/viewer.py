#!/usr/bin/env python
# ############################################################
# real time viewer for cAER via TCP stream
# author  Federico Corradi - federico.corradi@inilabs.com
# ############################################################
import numpy, glumpy
import socket
import struct
import time
import threading
import Queue
import logging
import numpy as np
from glumpy import app, gl, gloo, library
from glumpy.transforms import PanZoom, Position

import caer_communication

vertex = """
    uniform vec4 viewport;
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    varying vec2 v_pixcoord;
    varying vec2 v_quadsize;
    void main()
    {
        gl_Position = <transform>;
        v_texcoord = texcoord;
        v_quadsize = viewport.zw * <transform.panzoom_scale>;
        v_pixcoord = texcoord * v_quadsize;
    }
"""

fragment = """
#include "markers/markers.glsl"
#include "antialias/antialias.glsl"

uniform sampler2D data;
uniform vec2 data_shape;
varying vec2 v_texcoord;
varying vec2 v_quadsize;
varying vec2 v_pixcoord;

void main()
{
    float rows = data_shape.x;
    float cols = data_shape.y;
    float v = texture2D(data, v_texcoord).r;

    vec2 size = v_quadsize / vec2(cols,rows);
    vec2 center = (floor(v_pixcoord/size) + vec2(0.5,0.5)) * size;
    float d = marker_square(v_pixcoord - center, .9*size.x);
    gl_FragColor = filled(d, 1.0, 1.0, vec4(v,v,v,1));
}
"""

class ProducerThread(threading.Thread):
    def __init__(self, control, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name
        self.control = control
        self.control.open_communication_data()

    def run(self):
        while True:
            if not q.full():
                item = self.control._streaming()
                if(item != None):
                    q.put(item)
        return

                  
if __name__ == "__main__":
    # init control class and open communication

    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-9s) %(message)s',)
    BUF_SIZE = 4096*20
    xdim = 240
    ydim = 180
    zoom_factor  = 2

    q = Queue.Queue(BUF_SIZE)
    qprogram = Queue.Queue(BUF_SIZE)
    window = app.Window(width=xdim*zoom_factor, height=ydim*zoom_factor, color=(1,1,1,1))

    def matrix_active(x, y, pol):
        matrix = np.zeros([xdim, ydim])
        if(len(x) == len(y)):
            for i in range(len(x)):
                if(y[i] < ydim and x[i] < xdim):
                    matrix[x[i], y[i]] = pol[i]*0.5+0.1  # matrix[x[i],y[i]] + pol[i]
        else:
            print("error x,y missmatch")
        return matrix

    @window.event
    def on_draw(dt):
        window.clear()
        program.draw(gl.GL_TRIANGLE_STRIP)
        if not q.empty():
            item = q.get()
            eventtype = struct.unpack('H',item[0:2])[0]
            eventsource = struct.unpack('H',item[2:4])[0]
            eventsize = struct.unpack('I',item[4:8])[0]
            eventoffset = struct.unpack('I',item[8:12])[0]
            eventtsoverflow = struct.unpack('I',item[12:16])[0]
            eventcapacity = struct.unpack('I',item[16:20])[0]
            eventnumber = struct.unpack('I',item[20:24])[0]
            eventvalid = struct.unpack('I',item[24:28])[0]
            if(eventtype == 1):  
                counter = 28
                x_addr_tot = []
                y_addr_tot = []
                pol_tot = []
                while(item[counter:counter + eventsize]):  # loop over all event packets
                    aer_data = struct.unpack('I', item[counter:counter + 4])[0]
                    timestamp = struct.unpack('I', item[counter + 4:counter + 8])[0]
                    x_addr = (aer_data >> 17) & 0x00007FFF
                    y_addr = (aer_data >> 2) & 0x00007FFF
                    pol = (aer_data >> 1) & 0x00000001
                    counter = counter + 8
                    #print x_addr, y_addr
                    x_addr_tot.append(x_addr)
                    y_addr_tot.append(y_addr)
                    pol_tot.append(pol)
                matrix =  matrix_active(x_addr_tot, y_addr_tot, pol_tot)
                #if(y_addr < ydim and x_addr  < xdim):
                program['data'] = matrix

    @window.event
    def on_key_press(key, modifiers):
        if key == app.window.key.SPACE:
            transform.reset()

    @window.event
    def on_resize(width, height):
        program['viewport'] = 0, 0, width, height

    program = gloo.Program(vertex, fragment, count=4)
    n = 240
    program['position'] = [(-1,-1), (-1,1), (1,-1), (1,1)]
    program['texcoord'] = [( 0, 1), ( 0, 0), ( 1, 1), ( 1, 0)]
    program['data'] = np.random.uniform(0,1,(xdim,ydim))
    program['data_shape'] = program['data'].shape[:2]
    transform = PanZoom(Position("position"),aspect=1)
    program['transform'] = transform
    window.attach(transform)    
    control = caer_communication.caer_communication(host='localhost')   
    p = ProducerThread(control, name='producer')
    p.start()
    app.run(framerate=190)


  
