; =====================================================================
; PDF Master Pro - Ultimate Edition
; Professional Inno Setup 7 Installer Script
; Lead Architect: Eng. Mohamed Shaheed
; =====================================================================

#define MyAppName "PDF Master Pro - Ultimate Edition"
#define MyAppVersion "3.5.0"
#define MyAppPublisher "Eng. Mohamed Shaheed"
#define MyAppExeName "PDFMasterPro.exe"

[Setup]
AppId={{D37B5C72-87F1-4F95-9472-E4CA15A17F20}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\PDF Master Pro
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=PDFMasterPro_Ultimate_Setup_v3.5.0
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
DisableProgramGroupPage=auto
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "associate_pdf"; Description: "ربط وفتح ملفات PDF تلقائياً بواسطة PDF Master Pro"; GroupDescription: "تكامل النظام (System Integration):"

[Files]
Source: "dist\PDFMasterPro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "TEST_REPORT.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Registry]
; PDF File Association (Optional task)
Root: HKA; Subkey: "Software\Classes\.pdf\OpenWithProgids"; ValueType: string; ValueName: "PDFMasterPro.Document"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate_pdf
Root: HKA; Subkey: "Software\Classes\PDFMasterPro.Document"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey; Tasks: associate_pdf
Root: HKA; Subkey: "Software\Classes\PDFMasterPro.Document\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Flags: uninsdeletekey; Tasks: associate_pdf
Root: HKA; Subkey: "Software\Classes\PDFMasterPro.Document\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey; Tasks: associate_pdf

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
