function downloadMonSeqFPGAcode(usbinterface)

here=cd;
cd ../../../../USB2AERmapper/FPGA/MapperProject_ISE6

usbinterface.downloadFPGAFirmware('usbaer_top_level.bin')

cd(here)