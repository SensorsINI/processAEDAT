#include "mex.h"
#include <string.h>

//----------------------------------------------------------------------------------

void mexFunction( int nlhs, mxArray *plhs[],
                  int nrhs, const mxArray *prhs[])
{

  int Error=0;
  char filename[80];
  unsigned long dato;
  int i,j;
  FILE *f;
  int x,y,xi,yi;

  sprintf(filename, "demo1ret.bin");
  f=fopen(filename,"wb");

  for (xi=0;xi<256;xi++)
	for(yi=0;yi<256;yi++)
		for (i=0;i<8;i++)
       	{
					//para cada posible repeticion programo la salida
					// el ultimo debe tener el bit 16 a 1
					if (i==0){
						dato=0xff; //probabilidad
						dato=dato<<8;
						dato=dato+0x01; //es el ultimo y sin delay.
						dato=dato<<8;
						x=xi;
						y=yi;
						}
                    else dato = 0xff0100;
/*					if (i==1){
						dato=0x55; //probabilidad
						dato=dato<<8;
						dato=dato+0x02; //no el el ultimo
						dato=dato<<8;
						x=(xi/2)+64;
						y=yi/2;
						}
					if (i==2){
						dato=0x14; //probabilidad
						dato=dato<<8;
						dato=dato+0x02; //no el el ultimo
						dato=dato<<8;
						x=xi/2;
						y=(yi/2)+64;
						}
					if (i==3){
						dato=0xff; //probabilidad
						dato=dato<<8;
						dato=dato+0x03; //no el el ultimo
						dato=dato<<8;
						y=(xi/2)+64;
						x=(yi/2)+64;
						}
					if (i==4){
						dato=0xff; //probabilidad
						dato=dato<<8;
						dato=dato+0; //no el el ultimo
						dato=dato<<8;
						x=0xff;//xi;
						y=0xff;//yi+32;
						}
					if (i==5){
						dato=0x80; //probabilidad
						dato=dato<<8;
						dato=dato+0; //no el el ultimo
						dato=dato<<8;
						x=0xff;//xi;
						y=0xff;//yi+32;
						}
					if (i==6) {
						dato=0x40; //probabilidad
						dato=dato<<8;
						dato=dato+0; //no el el ultimo
						dato=dato<<8;
						x=0xff;//xi+32;
						y=0xff;//yi+32;
						}
					if (i==7) {
						dato=0x40; //probabilidad
						dato=dato<<8;
						dato=dato+1; //no el el ultimo
						dato=dato<<8;
						x=0xff;//xi+32;
						y=0xff;//yi+32;
						}
                    */

					dato=dato+x;
					dato=dato<<8;
					dato=dato+y;

					//if (!(yi%2) || !(xi%2)) dato =0x0001FFFF;
					//printf("%u\n",dato);

                    fwrite(&dato,sizeof(unsigned long),1,f);

            }
  fclose(f);
  puts(filename);

  plhs[0]=mxCreateScalarDouble((double) Error);
}
