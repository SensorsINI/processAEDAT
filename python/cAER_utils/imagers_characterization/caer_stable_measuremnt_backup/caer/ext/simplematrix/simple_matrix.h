/*
*  essential library that deals with matrix indexing
*  federico.corradi@inilabs.com
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* simple macro definitions*/
#define MIN(a,b) (((a)<(b))?(a):(b))
#define MAX(a,b) (((a)>(b))?(a):(b))

typedef struct ImageCoordinate {
   int x;
   int y;
   int index;
   float * image_data;
   int sizeX;
   int sizeY;
}ImageCoordinate;

void calculateIndex(ImageCoordinate *coordinates, int columns,int x,int  y);
void calculateCoordinates(ImageCoordinate *coordinates, int index,int columns, int rows);
void ImageCoordinateInit(ImageCoordinate *ts, int sizex, int sizey, int channels);
void normalizeImage(ImageCoordinate *ar);


