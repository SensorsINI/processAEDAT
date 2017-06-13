#!/bin/bash
set -e

WORKING_DIR="./recordings_training"
LIST_OF_EVENTS=(500 1000 2000 4000)
for EVENTS in "${LIST_OF_EVENTS[@]}"; do
    echo "Converting to AVI using ${EVENTS} accumulated events"
    mkdir "${WORKING_DIR}/avi${EVENTS}"
    find  ${WORKING_DIR} -maxdepth 2 -type f -name '*.aedat' -execdir dvs-slice-avi-writer.sh -dimx=64 -dimy=64 -grayscale=100 -quality=1.0 -normalize=true -rectify=true -numevents=${EVENTS} '{}' ';'
    echo "Conversion finished."
    cd "${WORKING_DIR}/aedat"
    #for file in ${WORKING_DIR}/aedat/*.avi; do ls $file; done
    rename -v "s/\.avi$/_${EVENTS}.avi/" *.avi
    mv *${EVENTS}.avi "../avi${EVENTS}/"
    echo "Moved AVI to corresponding folder"
    cd "../.."
done
