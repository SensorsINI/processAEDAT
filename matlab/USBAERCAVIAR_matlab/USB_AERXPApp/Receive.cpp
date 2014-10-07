//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "Receive.h"
#include "OpenByInterface.cpp"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormReceive *FormReceive;
double scale=1;
int tam=64;
unsigned int hardtimer=100;
int frmpersec = 0;
Graphics::TBitmap *imagen;

//---------------------------------------------------------------------------
__fastcall TFormReceive::TFormReceive(TComponent* Owner)
        : TForm(Owner)
{

}
//---------------------------------------------------------------------------
void __fastcall TFormReceive::FormShow(TObject *Sender)
{
int i;
imagen = new Graphics::TBitmap;
imagen->Height = 256;
imagen->Width = 256;
imagen->Monochrome = true;
imagen->Transparent = true;
imagen->PixelFormat = pf24bit;
Image1->Picture->Assign  (imagen);
DWORD	Error;
extern  char DevName0[28];

hDevice = OpenByInterface(DevName0);
if (hDevice != INVALID_HANDLE_VALUE)
        Timer1->Enabled = true;
else
        ShowMessage("Error opening device");
}
//---------------------------------------------------------------------------

void __fastcall TFormReceive::Timer1Timer(TObject *Sender)
{

int fila, col;
int x,y;
unsigned char *rowscan;

unsigned char buf[4096];

int i,size;

unsigned int valor;
unsigned long nWrite;
static unsigned int j=0;
  extern  char DevName0[28];

unsigned long longitud=4096, acumulaeventos;
unsigned int carga;
unsigned long integration_time=5000000;
integration_time=hardtimer*100000;

  Timer1->Enabled = false;
  Timer2->Enabled = true;
   frmpersec++;
 //if (!(j++%4))
        {
        //CloseHandle(hDevice);
         //hDevice = OpenByInterface(DevName0);
        //if (hDevice == INVALID_HANDLE_VALUE);// ShowMessage("Error opening device");
        }
        buf[0]='A';
        buf[1]='T';
        buf[2]='C';
        buf[3]= 2;   // comando 2 es leer RAM
        for(i=4;i<8;i++)
                buf[i]=(longitud>>(8*(i-4)))&0xff; //longitud.
        for(i=8;i<12;i++)
                buf[i]=(integration_time>>(8*(i-8)))&0xff; //longitud.
       // for(i=12;i<24;i++)
       //          buf[i]=0x00;
        WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);
       /*      if(nWrite<64)
                      {
                      ReadFile(hDevice, &buf, (unsigned long)longitud, &nWrite, NULL);
                      Timer1->Enabled = false;
                          CloseHandle(hDevice);
                          Close();
                        }     */
        //leer basurilla
        //ReadFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
        //for(i=0;i<longitud;i+=64)
        //ReadFile(hDevice, &buf[i], (unsigned long)64, &nWrite, NULL);
         ReadFile(hDevice, buf, (unsigned long)longitud, &nWrite, NULL);
         /*if(nWrite<longitud)
                      {
                      ReadFile(hDevice, &buf[nWrite], (unsigned long)longitud-nWrite, &nWrite, NULL);
                      /*Timer1->Enabled = false;
                          CloseHandle(hDevice);
                          Close();
                        }         */

  //       Image1->Picture->Assign  (imagen);
         Image1->Repaint();
 size=256/tam;
 acumulaeventos=0;
for (fila=0;fila<256;fila++)
{
        rowscan =(char *) Image1->Picture->Bitmap->ScanLine[fila];
        y=fila/size;//(256/tam);
        for(col =0; col<256; col ++)
        {
        x=col/ size;//(256/tam);
        valor=buf[tam*y+x]*scale;
        acumulaeventos=acumulaeventos+valor;
        if (valor>255) valor=255;
        rowscan[3*col]= valor;
        rowscan[3*col+1]= valor;
        rowscan[3*col+2]= valor;
         }
        }
 frmpersec++;   // Como depuración, para el cálculo real de marcos por segundo
 char cargatext [25];
 unsigned long cargadouble;
 cargadouble=(acumulaeventos*100)/16711680;

 ultoa(cargadouble,cargatext,10);
 Edit4->Text=cargatext;
 Timer1->Enabled = true;
}
//---------------------------------------------------------------------------

void __fastcall TFormReceive::FormClose(TObject *Sender,
      TCloseAction &Action)
{    Timer1->Enabled = false;
    CloseHandle(hDevice);
}
//---------------------------------------------------------------------------


void __fastcall TFormReceive::Button1Click(TObject *Sender)
{
 Timer1->Interval=Edit1->Text.ToInt();
 scale=Edit2->Text.ToDouble();
 tam=Edit3->Text.ToInt();
 hardtimer=Edit5->Text.ToInt();
 frmpersec=0;
 Timer2->Enabled = false;   //Para reiniciar la cuenta.
 Timer2->Enabled = true;
}
//---------------------------------------------------------------------------

void __fastcall TFormReceive::FormKeyPress(TObject *Sender, char &Key)
{
if (Key == VK_RETURN) Timer1->Interval=Edit1->Text.ToInt();

}
//---------------------------------------------------------------------------


void __fastcall TFormReceive::Timer2Timer(TObject *Sender)
{
Label8->Caption = FloatToStrF(frmpersec/2,ffFixed,4,0);
frmpersec=0;
}
//---------------------------------------------------------------------------

