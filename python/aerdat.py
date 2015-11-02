import struct
import numpy as np
import scipy as sp

def loadaerdat(datafile='/tmp/aerout.dat', stas=None, nEvents=None, datatype="II"):
	aerdatafh = open(datafile, 'rb')
	k = 0

	while aerdatafh.readline()[0] == "#":
		k += 1
		continue
	
	tmp = aerdatafh.read()
	n = len(tmp) / struct.calcsize('>' + datatype)
	tmad = struct.unpack_from('>' + datatype * n, tmp)
	dat = np.array(tmad)
	dat = dat.reshape(dat.shape[0] / 2, 2)
	
	if nEvents == None:
		nEvents = n		
	if stas == None:
		return dat
	else:
		tm = np.concatenate([[0], sp.diff(dat[:nEvents, 1])])
		ad = stas.STAddrPhysicalExtract(dat[:nEvents, 0]).transpose()
		return [tm, ad]

def saveaerdat(tmadEvents, datafile=None, stas=None, nEvents=None, datatype="HH"):
	tmp = struct.pack('>' + datatype, *stas.STAddrPhysicalConstruct(tmadEvents))
	
	if datafile == None:
			return tmp
	else:
		fh = open(datafile, 'w')
		fh.write(tmp)
		fh.close()
		return None	
