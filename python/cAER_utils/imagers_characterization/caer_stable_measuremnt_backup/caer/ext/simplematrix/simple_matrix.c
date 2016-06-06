#include "simple_matrix.h"

void ImageCoordinateInit(ImageCoordinate *ts, int sizeX, int sizeY, int channel)
{
    /* Set ts options to be ready */
    ts->x = NULL;
    ts->y = NULL;
    ts->index = NULL;
    ts->sizeX = sizeX;
    ts->sizeY = sizeY;
    ts->image_data = (float*)malloc(sizeX*sizeY*channel);
}

void calculateIndex(ImageCoordinate *ar, int columns,int x,int  y){
    ar->index = x * columns + y;
    return;
}

void calculateCoordinates(ImageCoordinate *ar, int index,int columns, int rows){
    int i =0;
    //for each row
    for(i=0; i<rows; i++){
        //check if the index parameter is in the row
        if(index < (columns * i) + columns && index >= columns * i){
            //return x, y
	    ar->x = index - columns * i;
	    ar->y = i;
        }
    }
    return;
}

void normalizeImage(ImageCoordinate *ar){
    int i,j = 0;
    double max = -1;
    double min = 255.0;
    double tmp = 0.0;
    for(i=0; i<ar->sizeX; i++){
    	for(j=0; j<ar->sizeY; j++){
    		calculateIndex(ar, ar->sizeY, i, j);
		min = MIN(min,ar->image_data[ar->index]);
		max = MAX(max,ar->image_data[ar->index]);
        }
    }
    for(i=0; i<ar->sizeX; i++){
	for(j=0; j<ar->sizeY; j++){
		calculateIndex(ar, ar->sizeY, i, j);
		tmp = ((ar->image_data[ar->index]) - min) / (max - min)  ;
	 	ar->image_data[ar->index] = (tmp * (255));
	        //printf("data[%d] : %u x:%d y:%d\n" , ar->index, (unsigned char)ar->image_data[ar->index], i, j );
	}
    }
    //printf("sum %d\n", sum);
}

