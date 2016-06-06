/*
 *  accumulates a fixed number of events and generates png pictures
 *  it also displays png images when available
 *  federico.corradi@inilabs.com
 */

#include "imagestreamervisualizer.h"
#include "base/mainloop.h"
#include "base/module.h"
#include <allegro5/allegro_audio.h>
#include <allegro5/allegro_acodec.h>
 

static bool caerImagestreamerVisualizerInit(caerModuleData moduleData);
static void caerImagestreamerVisualizerRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerImagestreamerVisualizerExit(caerModuleData moduleData);

static struct caer_module_functions caerImagestreamerVisualizerFunctions = { .moduleInit =
	&caerImagestreamerVisualizerInit, .moduleRun = &caerImagestreamerVisualizerRun, .moduleConfig =
NULL, .moduleExit = &caerImagestreamerVisualizerExit };

void caerImagestreamerVisualizer(uint16_t moduleID, unsigned char * disp_img, const int disp_img_size,
	double * classific_results, int * classific_sizes, int max_img_qty) {
	caerModuleData moduleData = caerMainloopFindModule(moduleID, "ImageStreamerVisualizer");

	caerModuleSM(&caerImagestreamerVisualizerFunctions, moduleData, sizeof(struct imagestreamervisualizer_state), 5,
		disp_img, disp_img_size, classific_results, classific_sizes, max_img_qty);
}

static bool caerImagestreamerVisualizerInit(caerModuleData moduleData) {
	caerImagestreamerVisualizerState state = moduleData->moduleState;

	state->vis_state = caerVisualizerInit(&caerVisualizerRendererFrameEvents, NULL, IMAGESTREAMERVISUALIZER_SCREEN_WIDTH, IMAGESTREAMERVISUALIZER_SCREEN_HEIGHT, VISUALIZER_DEFAULT_ZOOM, false, moduleData);
	if (state->vis_state == NULL) {
		return (false);
	}

    if(!al_init()){
      fprintf(stderr, "failed to initialize allegro!\n");
      return -1;
    }
    if(!al_install_audio()){
      fprintf(stderr, "failed to initialize audio!\n");
      return -1;
    }
    if(!al_init_acodec_addon()) {
       fprintf(stderr, "failed to initialize audio codecs!\n");
       return -1;
    }
    if (!al_reserve_samples(1)){
      fprintf(stderr, "failed to reserve samples!\n");
      return -1;
    }
 

    return (true);
}

static void caerImagestreamerVisualizerExit(caerModuleData moduleData) {
	caerImagestreamerVisualizerState state = moduleData->moduleState;

	caerVisualizerExit(state->vis_state);
	state->vis_state = NULL;
}

static void caerImagestreamerVisualizerRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
	UNUSED_ARGUMENT(argsNumber);

	caerImagestreamerVisualizerState state = moduleData->moduleState;

	// Interpret variable arguments (same as above in main function).
	unsigned char * disp_img = va_arg(args, char *);
	const int DISPLAY_IMG_SIZE = va_arg(args, const int);
	double * classific_results = va_arg(args, double *);
	int * classific_sizes = va_arg(args, int *);
	int max_img_qty = va_arg(args, int);

	ALLEGRO_SAMPLE *sample=NULL;

	//create one frame event packet, one single frame
	caerFrameEventPacket my_frame_packet = caerFrameEventPacketAllocate(1, I16T(moduleData->moduleID), 0,
	IMAGESTREAMERVISUALIZER_SCREEN_WIDTH, IMAGESTREAMERVISUALIZER_SCREEN_HEIGHT, 3);
	//get that single frame
	caerFrameEvent my_frame = caerFrameEventPacketGetEvent(my_frame_packet, 0);

	// only proceed if we have a display image
	if (disp_img == NULL) {
		return;
	}
	unsigned char *small_img = disp_img;
	//now put stuff into the frame
	int c, counter;
	counter = 0;
	for (int i = 0; i < IMAGESTREAMERVISUALIZER_SCREEN_WIDTH; i++) {
		for (int y = 0; y < IMAGESTREAMERVISUALIZER_SCREEN_HEIGHT; y++) {
			c = i * DISPLAY_IMG_SIZE + y;
			//depending on results display image with different color
			if (*classific_results == 0) {
			    my_frame->pixels[counter] = (uint16_t) (small_img[c] << 8);
			    my_frame->pixels[counter+1] = (uint16_t) (small_img[c] << 8);
			    my_frame->pixels[counter+2] = (uint16_t) (small_img[c] << 8);
			}else{
			    my_frame->pixels[counter] = (uint16_t) (0);
			    my_frame->pixels[counter+1] = (uint16_t) ( (int)(small_img[c]* *classific_results) << 8);
			    my_frame->pixels[counter+2] = (uint16_t) (0);
			}
			counter += 3;
		}
	}

    if(*classific_results != 0){
        sample = al_load_sample(AUDIO_BEEP_FILE);
        al_reserve_samples(1);
        if (!sample) {
           printf( "Audio clip sample not loaded!\n" ); 
        }else{
            al_play_sample(sample, 100.0, 0.0,1.0, ALLEGRO_PLAYMODE_ONCE, 0);
            al_rest(0.06);
        }
        al_destroy_sample(sample);
    }
	//add info to the frame
	caerFrameEventSetLengthXLengthYChannelNumber(my_frame, IMAGESTREAMERVISUALIZER_SCREEN_WIDTH,
	IMAGESTREAMERVISUALIZER_SCREEN_HEIGHT, 3, my_frame_packet);
	//valido
	caerFrameEventValidate(my_frame, my_frame_packet);
	//update bitmap
	caerVisualizerUpdate(state->vis_state, &my_frame_packet->packetHeader);

	free(my_frame_packet);
}
