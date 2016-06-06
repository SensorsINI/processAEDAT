/* Caffe Interface for deep learning
*  Author: federico.corradi@inilabs.com
*/

// Choose your network and it will run in real-time :-)

// CAFFENET .. more than 1000 classes
//#define NET_MODEL "/home/user/inilabs/caffe/models/bvlc_reference_caffenet/deploy.prototxt";
//#define NET_WEIGHTS  "/home/user/inilabs/caffe/models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel";
//#define NET_MEAN "/home/user/inilabs/caffe/data/ilsvrc12/imagenet_mean.binaryproto";
//#define NET_VAL "/home/user/inilabs/caffe/data/ilsvrc12/synset_words.txt";

// MNIST
//#define NET_MODEL "/home/user/inilabs/caffe/examples/mnist/lenet.prototxt";
//#define NET_WEIGHTS  "/home/user/inilabs/caffe/examples/mnist/lenet_iter_5000.caffemodel";
//#define NET_MEAN "/home/user/inilabs/caffe/examples/mnist/mean.mean";
//#define NET_VAL "/home/user/inilabs/caffe/data/mnist/val.txt";

//  DVS FACE DETECTION ZFRACTAL
//#define NET_MODEL "/home/federico/space/inilabs/3rdparty/caffe/examples/faces_36x36/lenet.prototxt";
//#define NET_WEIGHTS  "/home/federico/space/inilabs/3rdparty/caffe/examples/faces_36x36/snapshots/newdb_lenet_15000_spikes_iter_99000.caffemodel";
//#define NET_MEAN "/home/federico/space/inilabs/3rdparty/caffe/examples/faces_36x36/mean.mean";
//#define NET_VAL "/home/federico/space/inilabs/3rdparty/caffe/examples/faces_36x36/val.txt";

// DVS FACE DETECTION - remember to enable save_png and set detTreshold   
#define NET_MODEL "modules/caffeinterface/caffe_models/faces_36x36/lenet.prototxt";
#define NET_WEIGHTS  "modules/caffeinterface/caffe_models/faces_36x36/_iter_510000.caffemodel";
#define NET_MEAN "modules/caffeinterface/caffe_models/faces_36x36/mean.mean";
#define NET_VAL "modules/caffeinterface/caffe_models/faces_36x36/val.txt";
