#ifndef IMAGESTREAMERVISUALIZER_H_
#define IMAGESTREAMERVISUALIZER_H_

#include "main.h"
#include "modules/visualizer/visualizer.h"

#define IMAGESTREAMERVISUALIZER_SCREEN_WIDTH 200
#define IMAGESTREAMERVISUALIZER_SCREEN_HEIGHT 200

#define THR 0.5

#define TESTING 0		// keyboard "r" or "t" (recording or testing) "s" (stop) real-time test network, stores images in /tmp/ as defined in header file .h
#define TRAINING_POSITIVES 1	// keyboard "p" (positives) record pngs and store them in positive folder
#define TRAINING_NEGATIVES 2	// keyboard "n" (negatives) record pngs and store them in negative folder
// keyboard "s" stop saving png, generations on visualizer keeps going
#define AUDIO_BEEP_FILE "modules/imagestreamervisualizer/beep5.ogg"  

static int8_t savepng_state = 0;     //default state -> do not save png
static int8_t mode = 0;		 //default mode -> do nothing

struct imagestreamervisualizer_state {
	caerVisualizerState vis_state;
	// save output files
	int8_t savepng;
	int8_t mode;
};

typedef struct imagestreamervisualizer_state *caerImagestreamerVisualizerState;

void caerImagestreamerVisualizer(uint16_t moduleID, unsigned char * disp_img, const int disp_img_size,
	double * classific_results, int * classific_sizes, int max_img_qty);

#endif /* IMAGESTREAMERVISUALIZER_H_ */
