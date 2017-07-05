#!/bin/bash
rm -rf CMakeCache.txt
rm -rf CMakeFiles
cmake -DDAVISFX3=1 -DENABLE_STATISTICS=1 -DENABLE_VISUALIZER=1 -DENABLE_NETWORK_OUTPUT=1
make -j 4
