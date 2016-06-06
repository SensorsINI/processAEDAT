/*
 *  accumulates a fixed number of events and generates png pictures
 *  it also displays png images when available
 *  federico.corradi@inilabs.com
 */
#include <limits.h>
#include <float.h>
#include "imagegenerator.h"
#include "base/mainloop.h"
#include "base/module.h"
#include "modules/statistics/statistics.h"
#include "ext/portable_time.h"
#include <string.h>

#include "main.h"
#include <libcaer/events/polarity.h>

/* federico's matrix minimal lib */
#include "ext/simplematrix/simple_matrix.h"

/* inlude std image library */
#include "ext/stblib/stb_image_write.h"
#include "ext/stblib/stb_image_resize.h"

#define TESTING 0  // keyboard "r" or "t" (recording or testing) "s" (stop) real-time test network, stores images in /tmp/ as defined in header file .h
#define TRAINING_POSITIVES 1 // keyboard "p" (positives) record pngs and store them in positive folder
#define TRAINING_NEGATIVES 2 // keyboard "n" (negatives) record pngs and store them in negative folder
#define FRAME_SAVE_MODE 3       // used for saving frames with the save_img function, the file name contains "_frame_"

// keyboard "s" stop saving png, generations on visualizer keeps going

//define if you want to save frames to disk into FRAME_IMG_DIRECTORY (for analyzing and debugging)
static bool SAVE_FRAME = false;

struct imagegenerator_state {
    uint32_t *eventRenderer;
    int16_t eventRendererSizeX;
    int16_t eventRendererSizeY;
    struct caer_statistics_state eventStatistics;
    //save output files
    int8_t savepng;
    int8_t mode;
    //image matrix
    int64_t **ImageMap;
    int32_t numSpikes; // after how many spikes will we generate an image
    int32_t spikeCounter; // actual number of spikes seen so far, in range [0, numSpikes]
    int32_t counterImg; // how many spikeImages did we produce so far
    int32_t counterFrame; // how many frames did we see so far
    int16_t sizeX;
    int16_t sizeY;
    // frame
    uint16_t *frameRenderer;
    int32_t frameRendererSizeX;
    int32_t frameRendererSizeY;
    int32_t frameRendererPositionX;
    int32_t frameRendererPositionY;

    enum caer_frame_event_color_channels frameChannels;
};

typedef struct imagegenerator_state *imagegeneratorState;

static bool caerImageGeneratorInit(caerModuleData moduleData);
static void caerImageGeneratorRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerImageGeneratorExit(caerModuleData moduleData);
static bool allocateImageMap(imagegeneratorState state, int16_t sourceID);

static struct caer_module_functions caerImageGeneratorFunctions = {.moduleInit =
    &caerImageGeneratorInit, .moduleRun = &caerImageGeneratorRun, .moduleConfig =
    NULL, .moduleExit = &caerImageGeneratorExit};

void caerImageGenerator(uint16_t moduleID, caerPolarityEventPacket polarity, char ** file_strings_classify,
    int max_img_qty, int classify_img_size, char **display_img_ptr, int display_img_size,
    caerFrameEventPacket frame, char ** frame_ptr, int* frame_w, int* frame_h) {

    caerModuleData moduleData = caerMainloopFindModule(moduleID, "ImageGenerator");

    caerModuleSM(&caerImageGeneratorFunctions, moduleData, sizeof (struct imagegenerator_state), 10,
            polarity, file_strings_classify, max_img_qty, classify_img_size, display_img_ptr, display_img_size, frame, frame_ptr, frame_w, frame_h);

    return;
}

static bool caerImageGeneratorInit(caerModuleData moduleData) {

    // Ensure numSpikes is set.
    imagegeneratorState state = moduleData->moduleState;
    sshsNodePutIntIfAbsent(moduleData->moduleNode, "numSpikes", 7000);
    state->numSpikes = sshsNodeGetInt(moduleData->moduleNode, "numSpikes");
    sshsNodePutByteIfAbsent(moduleData->moduleNode, "savepng", 0);
    state->savepng =  sshsNodeGetByte(moduleData->moduleNode, "savepng");
    sshsNodePutByteIfAbsent(moduleData->moduleNode, "mode", 0);
    state->mode =  sshsNodeGetByte(moduleData->moduleNode, "mode");

    return (true);
}

static void caerImageGeneratorExit(caerModuleData moduleData) {
    imagegeneratorState state = moduleData->moduleState;

    // Ensure render maps are freed.
    if (state->eventRenderer != NULL) {
        free(state->eventRenderer);
        state->eventRenderer = NULL;
    }

}

/*  Function: save_img
 *  ------------------
 *  saves an image img to disk.
 *  If saveForClassification, put filename in file_strings_classify[file_counter].
 *  All files that are added to file_strings_classify will be classified from caffe
 *
 *  imgCounter: number of images of this type (spike-images or frames) seen so far
 *  img: image to save
 *  size_w: width of image
 *  size_h: height of image
 *  file_strings_classify: collection of file strings (disk location), which will be classified
 *  state_mode: mode which defines the filename
 *  file_counter: how many files we added already to the file_strings_classify
 *  directory: disk directory to save img
 *  save_for_classification: if true, add filename to file_stings_classify, otherwise just save img to disk
 *  max_img_qty: maximal number of images that can be added to file_strings_classify
 *
 */

static bool save_img(int img_counter, char *img, int size_w, int size_h, char ** file_strings_classify, char state_mode, int file_counter, char *directory, bool save_for_classification, int max_img_qty) {

    char id_img[15];
    char ext[] = ".png"; // png output (possibles other formats supported by the library are bmp, ppm, TGA, psd, pnm, hdr, gif,..)
    char filename[255];
    strcpy(filename, directory);

    //check in which mode we are (testing/training/none)

    if (state_mode == FRAME_SAVE_MODE) {
        strcat(filename, "frame_");
    }
    else if (state_mode == TESTING) {
        strcat(filename, "testing_spikes_");
    } else if (state_mode == TRAINING_POSITIVES) {
        strcat(filename, "pos_spikes_");
    } else if (state_mode == TRAINING_NEGATIVES) {
        strcat(filename, "neg_spikes_");
    } else { //default
        strcat(filename, "img_");
    }
    sprintf(id_img, "%d", img_counter);
    strcat(filename, id_img); //append id_img
    strcat(filename, ext); //append extension

    //save file and print error message if error occurs
    if (stbi_write_png(filename, size_w, size_h, 1, img, size_w * 1) == 0) {
        printf("Error in function \"save_img\" (saving images to disk). Path may not be found");
        return (false);
    }

    if (save_for_classification && file_counter < max_img_qty) {
        //strdup allocates memory!
        file_strings_classify[file_counter] = strdup(filename);
        file_counter += 1;
    }
    return (true);
}

/*  Function: normalize_to_quadratic_image_map
 *  ------------------------------------------
 *  Takes a rectangular image_map of type int64_t (the accumulated spike image) and returns
 *  a normalized quadratic_image_map of type char in range [0,255].
 *  The area of the quadratic map is the center (in both directions) of the rectangular map
 *  (like cutting out quadratic part and discard everything outside of cutting region).
 *
 *  image_map: accumulated spike image, rectangular
 *  size_w: width of image_map
 *  size_h: height of image_map
 *  size_quad: size of quadratic image map
 *  quadratic_image_map: (return value) normalized quadratic center of image_map
 */

static bool normalize_to_quadratic_image_map(int64_t **image_map, int size_w, int size_h, int size_quad, unsigned char * quadratic_image_map) {

    //check if sizes match
    if (size_w < size_quad || size_h < size_quad) {
        printf("\n Error in normalize_quadratic_image_map, size_quad too big.\n");
        return (false);
    }

    /* Hot pixels and other huge noise disturb the normalization.
     * If std deviation of normalized pixel is out of range [-outlierCut, outlierCut],
     * the pixel is detected as outlier and is removed (set to mean).
     */
    float outlierCut = 7.0;

    //initialize parameters
    bool foundOutlier = false;
    uint8_t tmp;
    float tmp_v;
    float max_tmp_v = FLT_MIN;
    float min_tmp_v = FLT_MAX;
    float mean = 0.0;
    float std = 0.0;

    //x and y offset, to cut out centered window
    int x_offset = (size_w - size_quad) / 2;
    int y_offset = (size_h - size_quad) / 2;

    //create quadratic int64_t map from input image_map
    int64_t qmap[size_quad * size_quad];
    int itr = 0;
    for (int y = 0; y < size_quad; ++y) {
        for (int x = 0; x < size_quad; ++x) {

            //copy desired region
            qmap[itr] = image_map[x + x_offset][(y + y_offset) -1];
            //accumulate mean
            mean = mean + qmap[itr];
            ++itr;
        }
    }
    mean = mean / (size_quad * size_quad * 1.0);

    //find outliers from hot pixels / huge noise and cut them off if bigger than outlierCut
    for (int i = 0; i < size_quad * size_quad; ++i) {
        std = std + pow((qmap[i] - mean), 2);
    }
    std = pow((std / (size_quad * size_quad * 1.0)), 0.5);

    for (int i = 0; i < size_quad * size_quad; ++i) {

        tmp_v = ((((float) qmap[i]) - mean) / std);

        if (tmp_v > outlierCut || tmp_v < -outlierCut) {
            //if found an outlier, set it to mean
            foundOutlier = true;
            qmap[i] = mean;
        } else {
            max_tmp_v = MAX(tmp_v, max_tmp_v);
            min_tmp_v = MIN(tmp_v, min_tmp_v);
        }

    }

    if (!foundOutlier) {
        //if no outlier was detected, mean and std are still valid
        for (int i = 0; i < size_quad * size_quad; ++i) {
            tmp_v = ((((float) qmap[i]) - mean) / std);
            tmp = round(((tmp_v - min_tmp_v) / (max_tmp_v - min_tmp_v)) * 255.0);
            quadratic_image_map[i] = tmp & 0xFF; //uchar
        }
    } else { //we found an outlier
        //we need to calculate a new mean and std
        mean = 0.0;
        std = 0.0;
        max_tmp_v = FLT_MIN;
        min_tmp_v = FLT_MAX;

        // get mean
        for (int i = 0; i < size_quad * size_quad; ++i) {
            mean = mean + qmap[i];
        }
        mean = mean / (size_quad * size_quad * 1.0);

        // get std
        for (int i = 0; i < size_quad * size_quad; ++i) {
            std = std + pow((qmap[i] - mean), 2);
        }
        std = pow((std / (size_quad * size_quad * 1.0)), 0.5);

        // find max_tmp_v and min_tmp_v, needed to shift normalized values into region [0,255]
        for (int i = 0; i < size_quad * size_quad; ++i) {
            tmp_v = ((((float) qmap[i]) - mean) / std);
            max_tmp_v = MAX(tmp_v, max_tmp_v);
            min_tmp_v = MIN(tmp_v, min_tmp_v);
        }

        // normalize and shift into region [0,255]
        for (int i = 0; i < size_quad * size_quad; ++i) {

            tmp_v = ((((float) qmap[i]) - mean) / std);
            tmp = round(((tmp_v - min_tmp_v) / (max_tmp_v - min_tmp_v)) * 255.0);
            quadratic_image_map[i] = tmp & 0xFF; //uchar
        }

    }

    return (true);
}


/*  Function: normalize_image
 *  -------------------------
 *  Normalizes image and shifts values into region [0,255].
 *
 *  image: image to normalize
 *  size_w: width of image
 *  size_h: height of image
 */

static void normalize_image(unsigned char * image, int size_w, int size_h) {
    /* normalize png image [0,255] */
    uint8_t tmp;
    float tmp_v;
    float max_tmp_v = FLT_MIN;
    float min_tmp_v = FLT_MAX;
    float mean = 0;
    float std = 0;
    int max_a = INT_MIN;
    int min_a = INT_MAX;

    //calculate mean of image
    for (int x_loop = 0; x_loop < size_w * size_h * 1; ++x_loop) {
        max_a = MAX(max_a, image[x_loop]);
        min_a = MIN(min_a, image[x_loop]);
        mean = mean + image[x_loop];
    }
    mean = mean / (size_w * size_h * 1.0);

    //calculated std of image
    for (int x_loop = 0; x_loop < size_w * size_h * 1; ++x_loop) {
        std = std + pow((image[x_loop] - mean), 2);
    }
    std = pow((std / (size_w * size_h * 1.0)), 0.5);

    //calculate MAX and MIN of normalized image, to shift into range [0,255]]
    for (int x_loop = 0; x_loop < size_w * size_h * 1; ++x_loop) {
        tmp_v = ((((float) image[x_loop]) - mean) / std);
        max_tmp_v = MAX(tmp_v, max_tmp_v);
        min_tmp_v = MIN(tmp_v, min_tmp_v);
    }

    //normalize and shift into range [0,255]]
    for (int x_loop = 0; x_loop < size_w * size_h * 1; ++x_loop) {
        tmp_v = ((((float) image[x_loop]) - mean) / std);
        tmp = round(((tmp_v - min_tmp_v) / (max_tmp_v - min_tmp_v)) * 255.0);
        image[x_loop] = tmp & 0xFF; //uchar
    }
}


/*  Function: cut_out_window_from_image
 *  -----------------------------------
 *  (not used so far)
 *
 *  Cuts out a sub-image (window) form an image. The position of the window/sub-image is defined
 *  by its top left corner. The top-left-corner-coordinates have to be chosen, so that the sub image
 *  is still completely covered by the original image.
 *
 *  image: image, from which the window is cut out
 *  imageX: size of image in X direction
 *  imageY: size of image in Y direction
 *  window: (return value) sub-image, which is cut out form image
 *  windowX: size of window in X direction
 *  windowY: size of window in Y direction
 *  windowTopLeftCornerX: x-coordinate (of top left corner of window) in original image
 *  windowTopLeftCornerY: y-coordinate (of top left corner of window) in original image
 *
 */
static bool cut_out_window_from_image(unsigned char *image, int imageX, int imageY, unsigned char *window, int windowX, int windowY,
        int windowTopLeftCornerX, int windowTopLeftCornerY) {

    // check sizes and position of window
    if (windowTopLeftCornerX < 0 || windowTopLeftCornerY < 0 ||
            imageX < 1 || imageY < 1 || windowX < 1 || windowY < 1 ||
            windowTopLeftCornerX + windowX - 1 >= imageX || windowTopLeftCornerY + windowY - 1 >= imageY) {
        printf("\nError in cutOutWindowFromImage, sizes do not match.\n");
        return (false);
    }

    for (int y = 0; y < windowY; y++) {
        for (int x = 0; x < windowX; x++) {

            window[y * windowX + x] = image[(windowTopLeftCornerY + y) * imageX + (windowTopLeftCornerX + x)];
        }
    }
    return (true);
}

static void caerImageGeneratorRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
    UNUSED_ARGUMENT(argsNumber);

    // Interpret variable arguments (same as above in main function).
    caerPolarityEventPacket polarity = va_arg(args, caerPolarityEventPacket);
    unsigned char ** file_strings_classify = va_arg(args, unsigned char **);
    int MAX_IMG_QTY = va_arg(args, int);
    int CLASSIFY_IMG_SIZE = va_arg(args, int);
    unsigned char ** display_img_ptr = va_arg(args, unsigned char **);
    int DISPLAY_IMG_SIZE = va_arg(args, int);
    caerFrameEventPacket frame = va_arg(args, caerFrameEventPacket);
    unsigned char ** frame_ptr = va_arg(args, unsigned char **);
    int * FRAME_W = va_arg(args, int *);
    int * FRAME_H = va_arg(args, int *);

    //counter for saved images (and corresponding file strings) which are handed to caffe CNN
    int file_string_counter = 0;

    // Only process packets with content.
    // what if content is not a polarity event?
    if (polarity == NULL && frame == NULL) {
        return;
    }

    //update module state
    imagegeneratorState state = moduleData->moduleState;
    state->savepng = sshsNodeGetByte(moduleData->moduleNode, "savepng");
    state->mode = sshsNodeGetByte(moduleData->moduleNode, "mode");

    // If the map is not allocated yet, do it.
    if (state->ImageMap == NULL) {
        if (!allocateImageMap(state, caerEventPacketHeaderGetEventSource(&polarity->packetHeader))) {
            // Failed to allocate memory, nothing to do.
            caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to allocate memory for ImageMap.");
            return;
        }
    }

    /* **** FRAME SECTION START *** */
    // initialize Frame
    if (frame != NULL) {
        caerFrameEvent currFrameEvent;

        //get latest event packages
        for (int32_t i = caerEventPacketHeaderGetEventNumber(&frame->packetHeader) - 1; i >= 0; i--) {
            currFrameEvent = caerFrameEventPacketGetEvent(frame, i);

            // Only operate on the last valid frame.
            if (caerFrameEventIsValid(currFrameEvent)) {
                // Copy the frame content to the permanent frameRenderer.
                // Use frame sizes to correctly support small ROI frames.
                state->frameRendererSizeX = caerFrameEventGetLengthX(currFrameEvent);
                state->frameRendererSizeY = caerFrameEventGetLengthY(currFrameEvent);
                state->frameRendererPositionX = caerFrameEventGetPositionX(currFrameEvent);
                state->frameRendererPositionY = caerFrameEventGetPositionY(currFrameEvent);
                state->frameChannels = caerFrameEventGetChannelNumber(currFrameEvent);

                state->frameRenderer = caerFrameEventGetPixelArrayUnsafe(currFrameEvent);

                break;
            }
        }

        if (state->frameRenderer != NULL) {

            //cast frame to unsigned char and return it in frame_ptr
            *frame_ptr = (unsigned char*) malloc(state->frameRendererSizeX * state->frameRendererSizeY * 1);
            if (*frame_ptr == NULL) {
		        caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to allocate *frame_ptr.");
		        return;
            }
            *FRAME_W = state->frameRendererSizeX;
            *FRAME_H = state->frameRendererSizeY;

            unsigned char *frame_img;
            frame_img = *frame_ptr;
            for (int frame_loop = 0; frame_loop < state->frameRendererSizeX * state->frameRendererSizeY * 1; ++frame_loop) {
                frame_img[frame_loop] = (state->frameRenderer[frame_loop] >> 8) & 0xFF;
            }

            //save frame if desired, do NOT classify on frame (at the moment)
            if (state->savepng == 1 && SAVE_FRAME) {
                if (!save_img(state->counterFrame, frame_img, state->frameRendererSizeX, state->frameRendererSizeY, file_strings_classify, FRAME_SAVE_MODE, -1, FRAME_IMG_DIRECTORY, false, MAX_IMG_QTY)){
                    caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to save image.");
                    return;
                }
            }

            state->counterFrame += 1;
        }

    }

    /* **** FRAME SECTION END *** */

    /* **** SPIKE SECTION START *** */
    if (polarity != NULL){
	    // Iterate over events and accumulate them
	    CAER_POLARITY_ITERATOR_VALID_START(polarity)

	    // Get coordinates and polarity (0 or 1) of latest spike.
	    uint16_t x = caerPolarityEventGetX(caerPolarityIteratorElement);
	    uint16_t y = caerPolarityEventGetY(caerPolarityIteratorElement);
	    int pol = caerPolarityEventGetPolarity(caerPolarityIteratorElement);
	    int x_loop = 0;
	    int y_loop = 0;

	    //Update image Map
	    if (pol == 0) {
		if (state->ImageMap[x][y] != INT64_MIN) {
		    state->ImageMap[x][y] = state->ImageMap[x][y] - 1;
		}
	    } else {
		if (state->ImageMap[x][y] != INT64_MAX) {
		    state->ImageMap[x][y] = state->ImageMap[x][y] + 1;
		}
	    }
	    state->spikeCounter += 1;

	    //If we saw enough spikes, generate Image from ImageMap.
	    if (state->spikeCounter >= state->numSpikes) {

		unsigned char *quadratic_image_map;
		quadratic_image_map = (unsigned char*) malloc(SIZE_QUADRATIC_MAP * SIZE_QUADRATIC_MAP * 1);
		if (quadratic_image_map == NULL) {
			caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to allocate quadratic_image_map.");
			return;
		}
		//nomalize image map and copy it into quadratic image_map [0,255]
		if (!normalize_to_quadratic_image_map(state->ImageMap, state->sizeX, state->sizeY, SIZE_QUADRATIC_MAP, quadratic_image_map)){
		    caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to generate quadratic image map.");
		    return;
		};

		// if Recording key (R) or testing key (T) is pressed, write image for classification to disk
		if (state->savepng == 1) {

		    //create classify_img with desired CLASSIFY_IMG_SIZE (input size of CNN)
		    unsigned char *classify_img;
		    classify_img = (unsigned char*) malloc(CLASSIFY_IMG_SIZE * CLASSIFY_IMG_SIZE * 1);
		    if (classify_img == NULL) {
			    caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to allocate classify_img.");
			    return;
		    }
		    stbir_resize_uint8(quadratic_image_map, SIZE_QUADRATIC_MAP, SIZE_QUADRATIC_MAP, 0, classify_img, CLASSIFY_IMG_SIZE, CLASSIFY_IMG_SIZE, 0, 1);

		    //normalize before saving
		    normalize_image(classify_img, CLASSIFY_IMG_SIZE, CLASSIFY_IMG_SIZE);
		    if (!save_img(state->counterImg, classify_img, CLASSIFY_IMG_SIZE, CLASSIFY_IMG_SIZE, file_strings_classify, state->mode, file_string_counter, CLASSIFY_IMG_DIRECTORY, true, MAX_IMG_QTY)){
		        caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to save image.");
			return;
		    }
		    free(classify_img);
		}

		//Create small_img to display the image_map, return it (to main function) in display_img_ptr
		unsigned char *disp_img;
		*display_img_ptr = (unsigned char*) malloc(DISPLAY_IMG_SIZE * DISPLAY_IMG_SIZE * 1);
		if (*display_img_ptr == NULL) {
			caerLog(CAER_LOG_ERROR, moduleData->moduleSubSystemString, "Failed to allocate *display_img_ptr.");
			return;
		}
		disp_img = *display_img_ptr;
		stbir_resize_uint8(quadratic_image_map, SIZE_QUADRATIC_MAP, SIZE_QUADRATIC_MAP, 0, disp_img, DISPLAY_IMG_SIZE, DISPLAY_IMG_SIZE, 0, 1);
		normalize_image(disp_img, DISPLAY_IMG_SIZE, DISPLAY_IMG_SIZE);

		//reset values
		for (x_loop = 0; x_loop < state->sizeX; x_loop++) {
		    for (y_loop = 0; y_loop < state->sizeY; y_loop++) {
		        state->ImageMap[x_loop][y_loop] = 0;
		    }
		}
		state->counterImg += 1;
		state->spikeCounter = 0;

		// free chunks of memory
		free(quadratic_image_map);
		state->frameRenderer = NULL;

	    }
	    CAER_POLARITY_ITERATOR_VALID_END
     }
    /* **** SPIKE SECTION END *** */
}


/*  Function: allocateImageMap
 *  -------------------------
 *  Allocates an ImageMap, so that pixels in ImageMap can be accessed with spike coordinates
 *  x and y by ImageMap[x][y].
 *
 *  state: imageGenerator state
 *  sourdeID: source identifier
 */
static bool allocateImageMap(imagegeneratorState state, int16_t sourceID) {
    // Get size information from source.
    sshsNode sourceInfoNode = caerMainloopGetSourceInfo((uint16_t) sourceID);
    int16_t sizeX = sshsNodeGetShort(sourceInfoNode, "dvsSizeX");
    int16_t sizeY = sshsNodeGetShort(sourceInfoNode, "dvsSizeY");

    // Initialize double-indirection contiguous 2D array, so that array[x][y]
    // is possible, see http://c-faq.com/aryptr/dynmuldimary.html for info.
    state->ImageMap = calloc((size_t) sizeX, sizeof (int64_t *));
    if (state->ImageMap == NULL) {
        return (false); // Failure.
    }

    state->ImageMap[0] = calloc((size_t) (sizeX * sizeY), sizeof (int64_t));
    if (state->ImageMap[0] == NULL) {
        free(state->ImageMap);
        state->ImageMap = NULL;

        return (false); // Failure.
    }

    for (size_t i = 1; i < (size_t) sizeX; i++) {
        state->ImageMap[i] = state->ImageMap[0] + (i * (size_t) sizeY);
    }

    // Assign max ranges for arrays (0 to MAX-1).
    state->sizeX = sizeX;
    state->sizeY = sizeY;

    // Init counters
    state->spikeCounter = 0;
    state->counterImg = 0;
    state->counterFrame = 0;

    return (true);
}

