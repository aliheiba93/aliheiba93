[Setup]
AppId={{A5F1B2D7-HEIBA-AI-ANALYSIS}
AppName=Heiba AI Analysis
AppVersion=0.1.0
AppPublisher=ENG Ali Heiba
DefaultDirName={autopf}\Heiba AI Analysis
ArchitecturesInstallIn64BitMode=x64
OutputBaseFilename=HeibaAI-Setup-x64
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\HeibaAI\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "dist\heiba-cli\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\Heiba AI Analysis"; Filename: "{app}\HeibaAI.exe"
Name: "{autodesktop}\Heiba AI Analysis"; Filename: "{app}\HeibaAI.exe"

[Run]
Filename: "{app}\HeibaAI.exe"; Description: "Launch Heiba AI Analysis"; Flags: nowait postinstall skipifsilent
