//---------------------------------------------------------------------------
#ifndef MainH
#define MainH
//---------------------------------------------------------------------------
#include <vcl\sysutils.hpp>
#include <vcl\windows.hpp>
#include <vcl\messages.hpp>
#include <vcl\sysutils.hpp>
#include <vcl\classes.hpp>
#include <vcl\graphics.hpp>
#include <vcl\controls.hpp>
#include <vcl\forms.hpp>
#include <vcl\dialogs.hpp>
#include <vcl\stdctrls.hpp>
#include <vcl\buttons.hpp>
#include <vcl\extctrls.hpp>
#include <vcl\menus.hpp>
#include <Classes.hpp>
#include <Dialogs.hpp>
#include <Menus.hpp>
#include <ExtDlgs.hpp>
#include <ComCtrls.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include "Trayicon.h"
#include "CSPIN.h"
#include <ExtCtrls.hpp>
//---------------------------------------------------------------------------
class TMainForm : public TForm
{
__published:
	TMainMenu *MainMenu;
	TMenuItem *FileOpenItem;
	TMenuItem *FileExitItem;
	TMenuItem *HelpAboutItem;
	TOpenDialog *OpenDialog;
	TSaveDialog *SaveDialog;
        TOpenPictureDialog *OpenPictureDialog;
        TMenuItem *UploadFile;
        TMenuItem *N2;
        TMenuItem *DownloadFromMapper;
        TProgressBar *pbProceso;
        TLabel *Label1;
        TEdit *txtWriteLenght;
        TLabel *Label3;
        TButton *btSend;
        TButton *btReceive;
        TEdit *txtReadLenght;
        TLabel *Label4;
        TEdit *txtReadBuffer;
        TEdit *txtWriteBuffer;
        TEdit *shDevNam;
        TMenuItem *Receiveimage;
        TLabel *Label6;
        TStatusBar *sbInformation;
        TGroupBox *GroupBox1;
        TRadioButton *SelDatalogger;
        TRadioButton *SelMapper;
        TLabel *Label2;
        TEdit *txtInitialAddress;
        TLabel *Label5;
        TEdit *txtDownloadLenght;
        TLabel *Label7;
        TEdit *txtsubcommands;
        TRadioButton *SelOthers;
        TButton *SendCommand;
        TPopupMenu *PopupMenu1;
	void __fastcall FileOpen(TObject *Sender);
	void __fastcall FileExit(TObject *Sender);
	void __fastcall HelpContents(TObject *Sender);
	void __fastcall HelpSearch(TObject *Sender);
	void __fastcall HelpAbout(TObject *Sender);
        void __fastcall UploadFileClick(TObject *Sender);
        void __fastcall txtWriteBufferChange(TObject *Sender);
        void __fastcall btSendClick(TObject *Sender);
        void __fastcall btReceiveClick(TObject *Sender);
        void __fastcall DownloadFromMapperClick(TObject *Sender);
        void __fastcall ReceiveimageClick(TObject *Sender);
        void __fastcall SendDescClick(TObject *Sender);
        void __fastcall SDevNameClick(TObject *Sender);
        void __fastcall FormActivate(TObject *Sender);
        void __fastcall txtsubcommandsOnExit(TObject *Sender);
        void __fastcall SendCommandClick(TObject *Sender);
        void __fastcall txtDownloadLenghtOnExit(TObject *Sender);

private:        // private user declarations
public:         // public user declarations
	virtual __fastcall TMainForm(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern TMainForm *MainForm;
//---------------------------------------------------------------------------
#endif
