//---------------------------------------------------------------------------
#include <vcl\vcl.h>
#pragma hdrstop

#include "Main.h"
#include "Receive.h"
#include <math.h>
#include <time.h>

#include "OpenByInterface.cpp"
//---------------------------------------------------------------------------
#pragma link "Trayicon"
#pragma link "CSPIN"
#pragma resource "*.dfm"
TMainForm *MainForm;
char DevName0[28]={"\\\\.\\Mapbul2Device0" };
int commands[16]={ 0 };
clock_t tmpini, tmpfin;


//---------------------------------------------------------------------------
__fastcall TMainForm::TMainForm(TComponent* Owner)
	: TForm(Owner)
{
}
//----------------------------------------------------------------------------
void __fastcall TMainForm::FileOpen(TObject *Sender)
{
//Subir firmware
	if (OpenDialog->Execute())
	{
 	DWORD	Error;
      	hDevice = OpenByInterface(DevName0);
        FILE *fileinput;
        unsigned long count = 0;
        unsigned long nWrite;
        unsigned long longitud, longtoload;
        char buf[167040];
        int i;
        unsigned int paso=16384;
        pbProceso->Position=0;
        if (hDevice == INVALID_HANDLE_VALUE)
	{
            ShowMessage("Error opening device");
	    // txtMensajes->Text ="ERROR opening device";
            sbInformation->Panels->Items[0]->Text = "ERROR opening device.";
	}
	else
	{
	      // txtMensajes->Text = "Device found, handle open.";
                fileinput = fopen(OpenDialog->FileName.c_str() ,"rb");
                if(fileinput) {

                        tmpini = clock();
                        sbInformation->Panels->Items[0]->Text = "Please wait...";sbInformation->Repaint();

                        fseek(fileinput,0,SEEK_END);
                        longitud = ftell(fileinput);
                        fseek(fileinput,0,SEEK_SET);

                        buf[0]='A';
                        buf[1]='T';
                        buf[2]='C';
                        buf[3]= 0;   // comando
                        for(i=4;i<8;i++)
                                buf[i]=(longitud>>(8*(i-4)))&0xff;
                        WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);

                      count = fread( buf, sizeof( char ), longitud, fileinput );
                      longtoload=64*(ceil(longitud/64));
                        if(nWrite != 64) ShowMessage("Received less than 64");
                        else
                        {
                                for(i=0;i<longtoload;i=i+paso)
                                {
	                        WriteFile(hDevice, buf+i, (unsigned long)paso, &nWrite, NULL);

                                pbProceso->Position = (i*100)/longitud;
                                pbProceso->Update();
                                }
                        }
                 }
                 fclose(fileinput);
                 CloseHandle(hDevice);

                 tmpfin = clock();
                 sbInformation->Panels->Items[0]->Text = "Elapsed time is "+ FloatToStrF((tmpfin-tmpini)/1000.000,ffFixed,3,3) + " seconds.";

	}
	}
}

//----------------------------------------------------------------------------
void __fastcall TMainForm::FileExit(TObject *Sender)
{
	Close();
}
//----------------------------------------------------------------------------
void __fastcall TMainForm::HelpContents(TObject *Sender)
{
	Application->HelpCommand(HELP_CONTENTS, 0);
}
//----------------------------------------------------------------------------
void __fastcall TMainForm::HelpSearch(TObject *Sender)
{
	Application->HelpCommand(HELP_PARTIALKEY, Longint(""));
}
//----------------------------------------------------------------------------
void __fastcall TMainForm::HelpAbout(TObject *Sender)
{
	//---- Add code to show program's About Box ----
}
//----------------------------------------------------------------------------
void __fastcall TMainForm::UploadFileClick(TObject *Sender)
{
	if (OpenDialog->Execute())
	{
 	DWORD	Error;
	hDevice = OpenByInterface(DevName0);
        FILE *fileinput;
        unsigned long count = 0;
        unsigned long counta = 0;
        unsigned long nWrite;
        unsigned long longitud,longtoload;
        unsigned long inicio;
        char buf[262144];
        int i;
        unsigned int paso = 262144;
        inicio = txtInitialAddress->Text.ToInt ();

        pbProceso->Position=0;

        if (hDevice == INVALID_HANDLE_VALUE)
	{
            ShowMessage("Error opening device");
	    //	txtMensajes->Text ="ERROR opening device";
            sbInformation->Panels->Items[0]->Text = "ERROR opening device.";
	}
	else
	{
	      //	txtMensajes->Text = "Device found, handle open.";
                fileinput = fopen(OpenDialog->FileName.c_str() ,"rb");
                if(fileinput) {
                        tmpini = clock();
                        sbInformation->Panels->Items[0]->Text = "Please wait...";sbInformation->Repaint();

                        fseek(fileinput,0,SEEK_END);
                        longitud = ftell(fileinput);
                        fseek(fileinput,0,SEEK_SET);
                        txtDownloadLenght->Text.sprintf("%l",longitud);

                        buf[0]='A';
                        buf[1]='T';
                        buf[2]='C';
                        buf[3]= 1;   // comando 1 es grabar RAM
                        for(i=4;i<8;i++)
                                buf[i]=(longitud>>(8*(i-4)))&0xff;

                        // Los siguientes bytes son los comandos que va a recibir la FPGA
                        if (SelMapper->Checked)
                        {   for(i=8;i<12;i++)
                                buf[i]=(inicio>>(8*(i-8)))&0xff;
                        }
                        if (SelDatalogger->Checked)
                        {  buf[8]=4;  // Comando de habilitación de escritura
                           buf[9]=3;  // Subcomando de establec. de la direcc
                           for(i=10;i<14;i++)
                                buf[i]=(inicio>>(8*(i-8)))&0xff;
                        }
                        if (SelOthers->Checked)
                        {  for(i=8;i<24;i++)
                                buf[i]=commands[i-8];
                        }

                        WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);

                        if(nWrite != 64) ShowMessage("Received less than 64");
                        else
                        {
                                while(!feof(fileinput))
                                {
                                count = fread( buf, sizeof( char ), paso, fileinput );
                                longtoload=64*(ceil(count/64));
                                counta=counta+count;
	                        WriteFile(hDevice, buf, (unsigned long)longtoload, &nWrite, NULL);
                                pbProceso->Position = counta*100/longitud;
                                pbProceso->Update();
                                }
                        }
                      /*while(!feof(fileinput))
                        {
                         count += fread( buf, sizeof( char ), 64, fileinput );
	                WriteFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
                        pbProceso->Position = count*100/longitud;
                        pbProceso->Update();
                        }*/
                 }
                 fclose(fileinput);
                 CloseHandle(hDevice);
                 tmpfin = clock();
                 sbInformation->Panels->Items[0]->Text = "Elapsed time is "+ FloatToStrF((tmpfin-tmpini)/1000.000,ffFixed,3,3) + " seconds.";

	}
	}
}
//---------------------------------------------------------------------------




void __fastcall TMainForm::txtWriteBufferChange(TObject *Sender)
{
txtWriteLenght->Text = strlen(txtWriteBuffer->Text.c_str());
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::btSendClick(TObject *Sender)
{
char *buffer;
char buf[64];
unsigned int i;
int num_packet;
DWORD	Error;
hDevice = OpenByInterface(DevName0);
unsigned long nWrite;
unsigned long longitud;
unsigned long inicio=0;

if (hDevice == INVALID_HANDLE_VALUE)
        {
	    //	txtMensajes->Text ="ERROR opening device";
            sbInformation->Panels->Items[0]->Text = "ERROR opening device";sbInformation->Repaint();
	}
else
	{
	      // txtMensajes->Text = "Device found, handle open.";
        tmpini = clock();
        sbInformation->Panels->Items[0]->Text = "Please wait...";sbInformation->Repaint();

        buffer= txtWriteBuffer->Text.c_str();
        longitud = strlen(buffer);

        // Enviamos comando

        buf[0]='A';
        buf[1]='T';
        buf[2]='C';
        buf[3]= 1;   // comando 1 es grabar RAM
        for(i=4;i<8;i++)
                buf[i]=(longitud>>(8*(i-4)))&0xff; //inicio.
        for(i=8;i<12;i++)
                buf[i]=(inicio>>(8*(i-8)))&0xff;
        WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);

        // vamos a enviar todos los datos
        for (i=0; i<longitud;i++)
        {
                buf[i%64]=buffer[i];
                if((i%64)==63)
                        WriteFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
        }
        // Si no era %64 habra quedado algo sin mandar, enviar paquete con basura al final
        if(longitud%64)
                WriteFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);

        CloseHandle(hDevice);
        tmpfin = clock();
        sbInformation->Panels->Items[0]->Text = "Elapsed time is "+ FloatToStrF((tmpfin-tmpini)/1000.000,ffFixed,3,3) + " seconds.";

        }
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::btReceiveClick(TObject *Sender)
{
char buffer[700000];      //Buffer donde leer
char buf[64];
int i;
int num_packet;
DWORD	Error;
hDevice = OpenByInterface(DevName0);
unsigned long nWrite;
unsigned long longitud;
unsigned long inicio =0;

if (hDevice == INVALID_HANDLE_VALUE)
        {
	    ShowMessage("ERROR opening device");
            sbInformation->Panels->Items[0]->Text = "ERROR opening device";
	}
else
	{
	      //txtMensajes->Text = "Device found, handle open.";
        tmpini = clock();
        sbInformation->Panels->Items[0]->Text = "Please wait...";sbInformation->Repaint();
        longitud = atoi(txtReadLenght->Text.c_str());
        txtReadBuffer->Text = "";


        // Enviamos comando
        buf[0]='A';
        buf[1]='T';
        buf[2]='C';
        buf[3]= 2;   // comando 2 es leer RAM
        for(i=4;i<8;i++)
                buf[i]=(longitud>>(8*(i-4)))&0xff; //longitud.
        for(i=8;i<12;i++)
                buf[i]=(inicio>>(8*(i-8)))&0xff;
        WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);
        //leer basurilla
        //ReadFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);


        // vamos a enviar todos los datos
        //for (i=0; i<longitud;i++)
        //{
        //        if((i%64)==0)
        //                ReadFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
        //        buffer[i]= buf[i%64];
        //}

        //buffer[i]=0;    // cadena ASCIIZ
         ReadFile(hDevice, buf, (unsigned long)longitud, &nWrite, NULL);
         buffer[longitud]=0;
        //txtReadBuffer->Text=buffer;
        CloseHandle(hDevice);
        tmpfin = clock();
        sbInformation->Panels->Items[0]->Text = "Elapsed time is "+ FloatToStrF((tmpfin-tmpini)/1000.000,ffFixed,3,3) + " seconds.";

        }
}
//---------------------------------------------------------------------------




//---------------------------------------------------------------------------

void __fastcall TMainForm::DownloadFromMapperClick(TObject *Sender)
{
unsigned long inicio;
unsigned long longitud;
char *filename;
char buf[262144]; //[64];
FILE *handle;
DWORD	Error;
unsigned long nWrite;
int i;


inicio = txtInitialAddress->Text.ToInt();
longitud = txtDownloadLenght->Text.ToInt();

if (longitud%64 != 0) {
      ShowMessage("Error Length. Must be multiple of 64");}
else
   {
   if (SaveDialog->Execute ())
   {
      filename = SaveDialog->FileName.c_str();
      handle=fopen(filename,"wb");
      hDevice = OpenByInterface(DevName0);

      if(handle && hDevice != INVALID_HANDLE_VALUE)
      {
          tmpini = clock();
          sbInformation->Panels->Items[0]->Text = "Please wait...";sbInformation->Repaint();
          pbProceso->Position = 0; pbProceso->Update();
           // Enviamos comando
           buf[0]='A';
           buf[1]='T';
           buf[2]='C';
           buf[3]= 2;   // comando 2 es leer RAM
           for(i=4;i<8;i++)
                   buf[i]=(longitud>>(8*(i-4)))&0xff; //longitud.

           if (SelMapper->Checked)
           {   for(i=8;i<12;i++)
               buf[i]=(inicio>>(8*(i-8)))&0xff;
           }
           if (SelDatalogger->Checked)
           {  buf[8]=1;  // Comando de configuración
              buf[9]=3;  // Subcomando de establec. de la direcc
              for(i=10;i<14;i++)
                 buf[i]=(inicio>>(8*(i-8)))&0xff;
           }
           if (SelOthers->Checked)
           {  for(i=8;i<24;i++)
              buf[i]=commands[i-8];
           }

           WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);
           //leer basurilla
           //ReadFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);

           // vamos a enviar todos los datos
           //ReadFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
           //for (i=64; i<longitud;i+=64)
           //{

           //     fwrite(buf,sizeof(char),64,handle);
           //     ReadFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
           //}
           //fwrite(buf,sizeof(char),longitud%64,handle);
           //Cambiamos ligeramente la estructura anterior para evitar leer
           //   un bloque de 256K cuando la longitud es menor a ésta.
           for (i=262144; i<=longitud;i+=262144)
           {
                ReadFile(hDevice, buf, (unsigned long)262144, &nWrite, NULL);
                fwrite(buf,sizeof(char),262144,handle);
                pbProceso->Position = i*100/longitud;
                pbProceso->Update();
            }
           ReadFile(hDevice, buf, (unsigned long)longitud%262144, &nWrite, NULL);
           fwrite(buf,sizeof(char),longitud%262144,handle);
           pbProceso->Position = 100;
       }
       CloseHandle(hDevice);
       fclose(handle);
       tmpfin = clock();
       sbInformation->Panels->Items[0]->Text = "Elapsed time is "+ FloatToStrF((tmpfin-tmpini)/1000.000,ffFixed,3,3) + " seconds.";
   }
   }
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::ReceiveimageClick(TObject *Sender)
{
       FormReceive->Show();
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::SendDescClick(TObject *Sender)
{
//char buffer[];      //Buffer donde leer
char buf[64];
int i;
int num_packet;
DWORD	Error;
hDevice = OpenByInterface(DevName0);
unsigned long nWrite;
unsigned long longitud;
unsigned long inicio =0;

//if (hDevice == INVALID_HANDLE_VALUE)
        {
  //	    ShowMessage("ERROR opening device");
	}
//else
	{
	      //	txtMensajes->Text = "Device found, handle open.";
        longitud=StrLen(txtWriteBuffer->Text.c_str());
        if(longitud>28)
                {ShowMessage("String too long");
                sbInformation->Panels->Items[0]->Text = "String too long.";}
        else
        {
        buf[0]='A';
        buf[1]='T';
        buf[2]='C';
        buf[3]= 3;   // comando 3 escribir descriptor
        for(i=4;i<8;i++)
                buf[i]=(longitud>>(8*(i-4)))&0xff;
        buf[8]=2*longitud+2;
        buf[9]= 3; //Desc String

        for (i=0;i<longitud;i++)
               {buf[10+2*i]=txtWriteBuffer->Text.c_str()[i];
                buf[11+2*i]=0;}
        i=10+2*i;
        while(i<64)buf[i++]=0;
        WriteFile(hDevice, buf, (unsigned long)64, &nWrite, NULL);
        }
        CloseHandle(hDevice);
        sbInformation->Panels->Items[0]->Text = "Done.";
        }
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::SDevNameClick(TObject *Sender)
{
strcpy( DevName0,"\\\\.\\" );
strcat(DevName0,txtWriteBuffer->Text.c_str());
shDevNam->Text=txtWriteBuffer->Text.c_str();
sbInformation->Panels->Items[0]->Text = "Done.";
}
//---------------------------------------------------------------------------

//---------------------------------------------------------------------------


void __fastcall TMainForm::FormActivate(TObject *Sender)
{
shDevNam->Text=DevName0+4;
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::txtsubcommandsOnExit(TObject *Sender)
{
char cad_aux[100];
char salida[100];
unsigned i, pos, posCommand;
bool flag, error;

   error = false;
   pos = 0;
   posCommand = 0;
   salida[0] = '\0';
   flag=false; // Bandera que indica si ya estoy tomando una cifra o estoy esperando.
   for (i=0;i<=txtsubcommands->Text.Length();i++) //Ojo el <= en vez de = es intencionado.
   {  if (isdigit(txtsubcommands->Text.c_str()[i])!=0 && i<txtsubcommands->Text.Length()) // Valor numérico
      {  if (posCommand == 16)
         {  ShowMessage("Warning. Too numbers. Trucating string.");
            break;
         }
         else
         {  if (flag==false) // Es un número y State = esperando (inicio de la cifra)
            {  flag = true; // Paso a State = recepción
               pos = i;
            }
         }
      }
      else   //Cualquier otro carácter es un separador
      {  if (flag == true) // Espacio en blanco y State = recepción (fin de la cifra)
         {  flag = false; // Paso a State = espera del siguiente número.
            strncpy(cad_aux,txtsubcommands->Text.c_str()+pos, i-pos); // y tomo el número recibido.
            commands[posCommand] = atoi(cad_aux);
            if (commands[posCommand]>255)
            {  commands[posCommand] = 0;
               error = true;
            }
            itoa(commands[posCommand],cad_aux,10);
            strcat(salida, cad_aux);
            if (posCommand<15) strcat(salida, " ");
            posCommand++;
         }
      }
   }
   while(posCommand<16)
   {  strcat(salida,"0");
      if (posCommand<15) strcat(salida," "); // A la última cifra no le sucede un espacio.
      commands[posCommand++]=0;
   }

   if (error == true)
      ShowMessage("There are numbers greater than 255. Setting to '0'.");
   txtsubcommands->Text=salida;
}
//---------------------------------------------------------------------------


void __fastcall TMainForm::SendCommandClick(TObject *Sender)
{
 	   DWORD Error;
           hDevice = OpenByInterface(DevName0);
           unsigned long nWrite;
           unsigned long longitud;
           char buf[64] = { 0 };
           int i;

           pbProceso->Position=0;
           if (hDevice == INVALID_HANDLE_VALUE)
      	   {
              ShowMessage("Error opening device");
              sbInformation->Panels->Items[0]->Text = "ERROR opening device.";
           }
      	   else
           {  longitud = 0;
              buf[0]='A';
              buf[1]='T';
              buf[2]='C';
              buf[3]= 2;   // comando 2 es leer ram pero la longitud es 0.
              for(i=4;i<8;i++)
                 buf[i]=0;
              for(i=8;i<24;i++)
                 buf[i]=commands[i-8];
              WriteFile(hDevice, buf,(unsigned long) 64, &nWrite, NULL);
              CloseHandle(hDevice);
              sbInformation->Panels->Items[0]->Text = "Done.";
              pbProceso->Position=100;
           }
}
//---------------------------------------------------------------------------


void __fastcall TMainForm::txtDownloadLenghtOnExit(TObject *Sender)
{
char cad_aux[100];
float value;
unsigned long valueint;
int cnt=0;

   while ((isdigit(txtDownloadLenght->Text.c_str()[cnt])!=0 || txtDownloadLenght->Text.c_str()[cnt]==',') && cnt<txtDownloadLenght->Text.Length()-1)
   cnt++;
   if (isdigit(txtDownloadLenght->Text.c_str()[cnt])!=0 || txtDownloadLenght->Text.c_str()[cnt]==',') // Lo que hay es una cifra
   {}
   else if (txtDownloadLenght->Text.c_str()[cnt]=='k' || txtDownloadLenght->Text.c_str()[cnt]=='K')
   {   strncpy(cad_aux,txtDownloadLenght->Text.c_str(),cnt); // y tomo el número recibido.
       cad_aux[cnt] = '\0';
       value = StrToFloat(cad_aux);   //Por si usa decimales
       value = value * 1024;
       txtDownloadLenght->Text = int(value);

   }
   else if (txtDownloadLenght->Text.c_str()[cnt]=='m' || txtDownloadLenght->Text.c_str()[cnt]=='M')
   {   strncpy(cad_aux,txtDownloadLenght->Text.c_str(),cnt); // y tomo el número recibido.
       cad_aux[cnt] = '\0';
       value = StrToFloat(cad_aux);   //Por si usa decimales
       value = value * 1024 * 1024;
       txtDownloadLenght->Text = int(value);
   }
   else
   {
      ShowMessage("Error. Invalid format");
      txtDownloadLenght->Text = 1024;
   }
}
//---------------------------------------------------------------------------


