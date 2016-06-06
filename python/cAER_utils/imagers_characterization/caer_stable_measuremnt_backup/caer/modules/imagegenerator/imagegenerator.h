#ifndef IMAGEGENERATOR_H_
#define IMAGEGENERATOR_H_

#include "main.h"

#include <libcaer/events/polarity.h>
#include <libcaer/events/frame.h>

#define IMAGEGENERATOR_SCREEN_WIDTH 400
#define IMAGEGENERATOR_SCREEN_HEIGHT 400

#define PIXEL_ZOOM 1

#define FRAME_IMG_DIRECTORY "/tmp/"
#define CLASSIFY_IMG_DIRECTORY "/tmp/"

/*Fabian*/
//#define FRAME_IMG_DIRECTORY "/home/user/inilabs/caer/images/frames/"
//#define CLASSIFY_IMG_DIRECTORY "/home/user/inilabs/caer/images/classify/"


//we cut out a quadratic part of the spike image from the rectangular input of the camera
#define SIZE_QUADRATIC_MAP 180

void caerImageGenerator(uint16_t moduleID, caerPolarityEventPacket polarity, char ** file_strings_classify,
	int max_img_qty, int classify_img_size, char **display_img_ptr, int display_img_size,
        caerFrameEventPacket frame, char ** frame_ptr, int* frame_w, int* frame_h);

#endif /* IMAGEGENERATOR_H_ */
