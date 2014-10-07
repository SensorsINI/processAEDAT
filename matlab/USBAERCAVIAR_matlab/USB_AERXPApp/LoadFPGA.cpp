//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop
USERES("LoadFPGA.res");
USEFORM("Main.cpp", MainForm);
USEFORM("Receive.cpp", FormReceive);
USEUNIT("OpenByInterface.cpp");
//---------------------------------------------------------------------------
WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int)
{
        try
        {
                 Application->Initialize();
                 Application->CreateForm(__classid(TMainForm), &MainForm);
                 Application->CreateForm(__classid(TFormReceive), &FormReceive);
                 Application->Run();
        }
        catch (Exception &exception)
        {
                 Application->ShowException(&exception);
        }
        return 0;
}
//---------------------------------------------------------------------------
