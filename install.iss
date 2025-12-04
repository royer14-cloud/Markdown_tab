; Script generado por el Inno Setup Script Wizard y adaptado para incluir todos los archivos de 'dist'.
; Asegúrate de que todos estos archivos y carpetas existan dentro del directorio del script (.iss) o en subdirectorios definidos.

#define MyAppName "Markdown Tab"
#define MyAppVersion "1.2"
#define MyAppPublisher "FRM"
#define MyAppURL "https://github.com/royer14-cloud/Markdown_tab"
#define MyAppExeName "MdTab.exe"

#include "CodeDependencies.iss"

[Setup]
; Información de la aplicación
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppContact=fmorinav@gmail.com
AppCopyright=Copyright (C) 2025 MRL
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
WindowVisible=yes

; Rutas de instalación
; Usamos {userappdata} para instalar por usuario, lo que no requiere permisos de administrador.
DefaultDirName={userappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=Output
OutputBaseFilename=MarkdownTab
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=2

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; --- Archivos sueltos en el directorio raíz de la aplicación ({app}) ---
; Source: hace referencia a la ubicación del archivo en tu sistema (asumiendo que están en la carpeta 'dist')
; DestDir: es el destino dentro de la instalación (en este caso, la carpeta principal de la app)

Source: "dist\Markdown Tab\MdTab.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Markdown Tab\icon.ico"; DestDir: "{app}"
Source: "dist\Markdown Tab\README.txt"; DestDir: "{app}"; Flags: isreadme

; --- Carpetas completas (config, icons, make) ---
; El flag 'recursesubdirs' asegura que se copien la carpeta y todos sus subarchivos.
; El asterisco Source: "dist\config\*" indica que tome todo el contenido de 'dist\config'.

; Copiar la carpeta de complementos
Source: "dist\Markdown Tab\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs createallsubdirs

[UninstallDelete]
Type: dirifempty; Name: "{app}\_internal"
Type: files; Name: "{app}\_internal\*.*"

[Icons]
; Icono del menú Inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Icono de desinstalación
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
; Icono de escritorio (depende de si el usuario lo marca en las tareas)
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Asociación de Tipo de Archivo (FTA) para .mdg
Root: "HKCR"; Subkey: ".mdg"; ValueType: string; ValueData: "MarkdownTab.mdgfile"; Flags: uninsdeletekey
; Define el tipo de archivo (nombre descriptivo)
Root: "HKCR"; Subkey: "MarkdownTab.mdgfile"; ValueType: string; ValueData: "Markdown Tab Document (.mdg)"; Flags: uninsdeletekey
; Define el ícono para archivos .mdg
Root: "HKCR"; Subkey: "MarkdownTab.mdgfile\DefaultIcon"; ValueType: string; ValueData: "{app}\icon.ico"
; Define el comando para abrir el archivo con MdTab.exe.
; El ""%1"" es crucial, ya que pasa la ruta completa del archivo al ejecutable.
Root: "HKCR"; Subkey: "MarkdownTab.mdgfile\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Run]
; Ejecutar la aplicación después de la instalación
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent


[Code]
function InitializeSetup: Boolean;
begin
    Dependency_AddDotNet40;
    Result := True;
end;