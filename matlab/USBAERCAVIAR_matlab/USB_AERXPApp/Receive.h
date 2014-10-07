//---------------------------------------------------------------------------

#ifndef ReceiveH
#define ReceiveH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
#include <Graphics.hpp>
#include <ComCtrls.hpp>
//---------------------------------------------------------------------------
class TFormReceive : public TForm
{
__published:	// IDE-managed Components
        TImage *Image1;
        TTimer *Timer1;
        TEdit *Edit1;
        TButton *Button1;
        TLabel *Label1;
        TEdit *Edit2;
        TLabel *Label2;
        TEdit *Edit3;
        TLabel *Label3;
        TEdit *Edit4;
        TLabel *Label4;
        TLabel *Label5;
        TLabel *Label6;
        TEdit *Edit5;
        TTimer *Timer2;
        TLabel *Label7;
        TLabel *Label8;
        void __fastcall FormShow(TObject *Sender);
        void __fastcall Timer1Timer(TObject *Sender);
        void __fastcall FormClose(TObject *Sender, TCloseAction &Action);
        void __fastcall Button1Click(TObject *Sender);
        void __fastcall FormKeyPress(TObject *Sender, char &Key);
        void __fastcall Timer2Timer(TObject *Sender);
private:	// User declarations
public:		// User declarations
        __fastcall TFormReceive(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TFormReceive *FormReceive;
//---------------------------------------------------------------------------
#endif
