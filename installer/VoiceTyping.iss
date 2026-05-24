; Inno Setup script for VoiceTyping installer
; Requires Inno Setup 6: https://jrsoftware.org/isinfo.php

#define MyAppName "VoiceTyping"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "VoiceTyping"
#define MyAppURL "https://github.com/ikaros230/VoiceTyping"
#define MyAppExeName "VoiceTyping.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer\output
OutputBaseFilename=VoiceTyping-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.LaunchProgram=Launch VoiceTyping
english.AdditionalIcons=Additional icons:
english.CreateDesktopIcon=Create a &desktop icon
english.StartupTask=Start VoiceTyping when Windows starts
english.StartupTaskDescription=Startup options:

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "{cm:StartupTask}"; GroupDescription: "{cm:StartupTaskDescription}"; Flags: unchecked

[Files]
Source: "..\dist\VoiceTyping\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent
