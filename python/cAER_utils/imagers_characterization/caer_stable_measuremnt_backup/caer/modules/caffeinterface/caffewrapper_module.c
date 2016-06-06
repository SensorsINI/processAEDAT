/* Caffe Interface cAER module
 *  Author: federico.corradi@inilabs.com
 */

#include "base/mainloop.h"
#include "base/module.h"
#include "wrapper.h"

struct caffewrapper_state {
	uint32_t *integertest;
	char * file_to_classify;
	double detThreshold;
	struct MyClass* cpp_class; //pointer to cpp_class_object
};

typedef struct caffewrapper_state *caffewrapperState;

static bool caerCaffeWrapperInit(caerModuleData moduleData);
static void caerCaffeWrapperRun(caerModuleData moduleData, size_t argsNumber, va_list args);
static void caerCaffeWrapperExit(caerModuleData moduleData);

static struct caer_module_functions caerCaffeWrapperFunctions = { .moduleInit = &caerCaffeWrapperInit, .moduleRun =
	&caerCaffeWrapperRun, .moduleConfig =
NULL, .moduleExit = &caerCaffeWrapperExit };

const char * caerCaffeWrapper(uint16_t moduleID, char ** file_string, double *classificationResults, int max_img_qty) {

    caerModuleData moduleData = caerMainloopFindModule(moduleID, "caerCaffeWrapper");
	caerModuleSM(&caerCaffeWrapperFunctions, moduleData, sizeof(struct caffewrapper_state), 3, file_string, classificationResults, max_img_qty);

	return (NULL);
}

static bool caerCaffeWrapperInit(caerModuleData moduleData) {

    	caffewrapperState state = moduleData->moduleState;
	sshsNodePutDoubleIfAbsent(moduleData->moduleNode, "detThreshold", 0.5);
	state->detThreshold = sshsNodeGetDouble(moduleData->moduleNode, "detThreshold");

	//Initializing caffe network..
	state->cpp_class = newMyClass();
	MyClass_init_network(state->cpp_class);

	return (true);
}

static void caerCaffeWrapperExit(caerModuleData moduleData) {
	caffewrapperState state = moduleData->moduleState;
	deleteMyClass(state->cpp_class); //free memory block
}

static void caerCaffeWrapperRun(caerModuleData moduleData, size_t argsNumber, va_list args) {
    UNUSED_ARGUMENT(argsNumber);
    caffewrapperState state = moduleData->moduleState;
    char ** file_string = va_arg(args, char **);
    double *classificationResults = va_arg(args, double*);
    int max_img_qty = va_arg(args, int);

    //update module state
    state->detThreshold = sshsNodeGetDouble(moduleData->moduleNode, "detThreshold");

    for (int i = 0; i < max_img_qty; ++i){
        if (file_string[i] != NULL) {
            MyClass_file_set(state->cpp_class, file_string[i], &classificationResults[i], state->detThreshold);
        }
    }

	return;
}
