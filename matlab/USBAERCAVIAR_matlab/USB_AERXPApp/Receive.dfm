object FormReceive: TFormReceive
  Left = 635
  Top = 189
  BorderIcons = [biSystemMenu]
  BorderStyle = bsSingle
  Caption = 'FormReceive'
  ClientHeight = 298
  ClientWidth = 360
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'MS Sans Serif'
  Font.Style = []
  OldCreateOrder = False
  Scaled = False
  OnClose = FormClose
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object Image1: TImage
    Left = 8
    Top = 15
    Width = 256
    Height = 256
    Center = True
  end
  object Label2: TLabel
    Left = 272
    Top = 48
    Width = 75
    Height = 13
    Caption = 'Gray level scale'
  end
  object Label3: TLabel
    Left = 272
    Top = 88
    Width = 20
    Height = 13
    Caption = 'Size'
  end
  object Label4: TLabel
    Left = 272
    Top = 128
    Width = 64
    Height = 13
    Caption = 'image charge'
  end
  object Label1: TLabel
    Left = 272
    Top = 8
    Width = 78
    Height = 13
    Caption = 'Timer Value (ms)'
  end
  object Label5: TLabel
    Left = 272
    Top = 168
    Width = 71
    Height = 13
    Caption = 'Hardware timer'
  end
  object Label6: TLabel
    Left = 272
    Top = 184
    Width = 49
    Height = 13
    Caption = 'Value (ms)'
  end
  object Label7: TLabel
    Left = 272
    Top = 226
    Width = 75
    Height = 13
    Caption = 'real frames/Sec'
  end
  object Label8: TLabel
    Left = 272
    Top = 243
    Width = 81
    Height = 17
    AutoSize = False
    Caption = '0'
    Color = clHighlightText
    ParentColor = False
  end
  object Edit1: TEdit
    Left = 272
    Top = 24
    Width = 81
    Height = 21
    TabOrder = 1
    Text = '100'
  end
  object Button1: TButton
    Left = 272
    Top = 267
    Width = 75
    Height = 25
    Caption = 'Update'
    Default = True
    TabOrder = 0
    OnClick = Button1Click
  end
  object Edit2: TEdit
    Left = 272
    Top = 64
    Width = 81
    Height = 21
    TabOrder = 2
    Text = '1'
  end
  object Edit3: TEdit
    Left = 272
    Top = 104
    Width = 81
    Height = 21
    TabOrder = 3
    Text = '64'
  end
  object Edit4: TEdit
    Left = 272
    Top = 144
    Width = 81
    Height = 21
    TabOrder = 4
    Text = '0'
  end
  object Edit5: TEdit
    Left = 272
    Top = 200
    Width = 81
    Height = 21
    TabOrder = 5
    Text = '100'
  end
  object Timer1: TTimer
    Enabled = False
    Interval = 100
    OnTimer = Timer1Timer
    Left = 224
    Top = 24
  end
  object Timer2: TTimer
    Enabled = False
    Interval = 2000
    OnTimer = Timer2Timer
    Left = 224
    Top = 72
  end
end
