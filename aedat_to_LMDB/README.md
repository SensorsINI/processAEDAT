## AEDAT to LMDB conversion

1.**aedat_to_avi.sh** is a bash script that takes all the .aedat recordings in the specified folder and converts them to .avi using jAER. The LIST_OF_EVENTS specifies what number of events you want to accumulate to produce one frame. 

2.**avi_to_lmdb.py** takes all available .avi files and compiles them in train and test LMDBs.
