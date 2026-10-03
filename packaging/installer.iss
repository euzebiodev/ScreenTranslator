; Instalador do Screen Translator (Inno Setup 6).
; Compilado por packaging\build_installer.ps1 apos o PyInstaller gerar
; dist\ScreenTranslator\ (app + dependencias Python + Tesseract embutido).

#define MyAppName "Screen Translator"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Euzebio"
#define MyAppExeName "ScreenTranslator.exe"

[Setup]
AppId={{F03A7293-2BDB-499C-BB62-B9F07071DD31}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=ScreenTranslator-Setup-{#MyAppVersion}
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos adicionais:"

[Files]
Source: "..\dist\ScreenTranslator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName} agora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Mantem o banco de dados de traducoes (%APPDATA%\ScreenTranslator) apos
; desinstalar, so remove arquivos temporarios gerados pelo app, se houver.
