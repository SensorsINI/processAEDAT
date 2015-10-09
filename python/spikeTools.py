# python script that gather auxiliary function to handle aedat files
# author Federico Corradi, Fabian Muller
from __future__ import division
import numpy as np
import scipy as sp
import loadaerdat
from matplotlib.pyplot import imshow, show, figure, arrow, plot, title
from matplotlib import pylab

V2 = "aedat" # current 32bit file format
time_resolution = 1e-6
size_frames = 32 
dim_to_estimates = 3
camera = "DAVIS240"
dim_multiplier = 1.6 
DataDir = '/home/federico/Dropbox/_/Data/Raw/Fabian'
filename="Female_Train_bad"

if camera == "DAVIS240":
    xsize=240
    ysize=180

# filename according to standards
datafile = DataDir + "/" + filename + "_all.aedat"

timestamps,xaddr,yaddr,pol = loadaerdat.loadaerdat(datafile=datafile, length=0, version=V2, debug=1, camera=camera);

def matrix_active(x,y, pol):
    matrix = np.zeros([256,256])
    if(len(x)==len(y)):  
        for i in range(len(x)):
            matrix[y[i],x[i]] = matrix[y[i],x[i]] + pol[i]#matrix[x[i],y[i]] + pol[i]
    else:
        print("error x,y missmatch")
    return matrix

def sub2ind(array_shape, rows, cols):
    return rows*array_shape[1] + cols

def ind2sub(array_shape, ind):
    ind[ind < 0] = -1
    ind[ind >= array_shape[0]*array_shape[1]] = -1
    rows = (ind.astype('int') / array_shape[1])
    cols = ind % array_shape[1]
    return (rows, cols)

def show_spike_density(xaddr, yaddr, camera='DAVIS240'):
    '''
    produce a density plot for davis camera
    '''
    import numpy as np
    import matplotlib.pyplot as plt
    import pylab
    from sklearn.preprocessing import normalize

    xaddr = np.loadtxt('data/xaddr_small.txt')
    yaddr = np.loadtxt('data/yaddr_small.txt')
    timestamps = np.loadtxt('data/timestamps_small.txt')
    pol = np.loadtxt('data/pol_small.txt')

    if(camera == 'DAVIS240'):
        xmin = 0   #np.min(xaddr) #assuming all pixels were active at least once
        xmax = 239 #np.max(xaddr)
        ymin = 0
        ymax = 179

    chunkdim = 3000
    nchunks = int(np.floor(len(xaddr)/chunkdim))
    ind_density = np.zeros([256,256])
    for i in range(nchunks):
        tmp = matrix_active(xaddr[(i*chunkdim):((i+1)*chunkdim)],yaddr[(i*chunkdim):((i+1)*chunkdim)], pol[(i*chunkdim):((i+1)*chunkdim)])
        ind_density = ind_density + tmp
        ind_density = normalize(ind_density, axis=1, norm='l1') 

    plt.imshow(np.rot90(ind_density.T), interpolation='nearest')    
    plt.show()

    return

def simple_frequency_spectrum(x):
    """
    Very simple calculation of frequency spectrum with no detrending,
    windowing, etc. Just the first half (positive frequency components) of
    abs(fft(x))
    """
    spec = np.absolute(np.fft.fft(x))
    spec = spec[:len(x)/2] # take positive frequency components
    spec /= len(x)         # normalize
    spec *= 2.0            # to get amplitudes of sine components, need to multiply by 2
    spec[0] /= 2.0         # except for the dc component
    return spec


def ccf(x, y, axis=None):
    """
	from neurotools
    Computes the cross-correlation function of two series x and y.
    Note that the computations are performed on anomalies (deviations from
    average).
    Returns the values of the cross-correlation at different lags.
        
    Inputs:
        x    - 1D MaskedArray of a Time series.
        y    - 1D MaskedArray of a Time series.
        axis - integer *[None]* Axis along which to compute (0 for rows, 1 for cols).
               If `None`, the array is flattened first.
    
    Examples:
        >> z= arange(1000)
        >> ccf(z,z)
    """
    assert x.ndim == y.ndim, "Inconsistent shape !"
#    assert(x.shape == y.shape, "Inconsistent shape !")
    if axis is None:
        if x.ndim > 1:
            x = x.ravel()
            y = y.ravel()
        npad = x.size + y.size
        xanom = (x - x.mean(axis=None))
        yanom = (y - y.mean(axis=None))
        Fx = np.fft.fft(xanom, npad, )
        Fy = np.fft.fft(yanom, npad, )
        iFxy = np.fft.ifft(Fx.conj()*Fy).real
        varxy = np.sqrt(np.inner(xanom,xanom) * np.inner(yanom,yanom))
    else:
        npad = x.shape[axis] + y.shape[axis]
        if axis == 1:
            if x.shape[0] != y.shape[0]:
                raise ValueError, "Arrays should have the same length!"
            xanom = (x - x.mean(axis=1)[:,None])
            yanom = (y - y.mean(axis=1)[:,None])
            varxy = np.sqrt((xanom*xanom).sum(1) * (yanom*yanom).sum(1))[:,None]
        else:
            if x.shape[1] != y.shape[1]:
                raise ValueError, "Arrays should have the same width!"
            xanom = (x - x.mean(axis=0))
            yanom = (y - y.mean(axis=0))
            varxy = np.sqrt((xanom*xanom).sum(0) * (yanom*yanom).sum(0))
        Fx = np.fft.fft(xanom, npad, axis=axis)
        Fy = np.fft.fft(yanom, npad, axis=axis)
        iFxy = np.fft.ifft(Fx.conj()*Fy,n=npad,axis=axis).real
    # We juste turn the lags into correct positions:
    iFxy = np.concatenate((iFxy[len(iFxy)/2:len(iFxy)],iFxy[0:len(iFxy)/2]))
    return iFxy/varxy 


spec = simple_frequency_spectrum(np.diff(timestamps[0:5000]),np.diff(timestamps[0:5000]))
