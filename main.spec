# -*- mode: python ; coding: utf-8 -*-

# Este es el archivo de especificación para PyInstaller.
# Puedes compilar tu aplicación con el siguiente comando en tu terminal:
# pyinstaller build.spec

# --- Análisis de la aplicación y sus dependencias ---
#
# a = Analysis(...) es donde PyInstaller escanea tu código fuente
# para encontrar todos los módulos y archivos necesarios.
block_cipher = None

a = Analysis(
    ['main.py'],  # Reemplaza 'main.py' con el nombre de tu archivo principal.
    pathex=['.'],
    binaries=[],
    datas=[
        ('icons/icon.png', 'icons'),  # Icono principal para la aplicación
        ('icons/light', 'icons/light'),  # Carpeta de iconos para el tema claro
        ('icons/dark', 'icons/dark'),    # Carpeta de iconos para el tema oscuro
        ('config/config.cfg', 'config'), # Configuracion de aplicacion
        ('config/dark.css', 'config'), # tema de CFG
        ('config/light.css', 'config'), # tema de CFG
		('make/tutorial/remove.exe', 'make/tutorial'), # carpeta del eliminador
		('make/tutorial/remove.exe.config', 'make/tutorial'), # config del eliminador
		('make/tutorial/example.mdg', 'make/tutorial'), # archivo del tutorial
		('make/tutorial/new.mdg', 'make/tutorial'), # archivo de muestra
		('make/chords', 'make/chords'), # carpeta de acordes
        ('make/fonts', 'make/fonts'), # carpeta de fuentes
        ('make/img', 'make/img') # carpeta de iconos tab
        
    ],
    hiddenimports=[
        'View',       # Importa explícitamente el módulo View
        'Dialog',     # Importa el modulo Dialog
        'load_dir',   # Importa el modulo abs_path
        'make.extPDF',  # Importa el módulo make.extPDF
        'make.export',  # Importa el módulo make.export
        'config.CFG',  # Importa el módulo MainPop
        'config.cmessagebox', # Importa el módulo show_info
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# --- Creación del ejecutable ---
#
# pyz = PYZ(...) crea un archivo comprimido de las dependencias.

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- Configuración del ejecutable (EXE) ---
#
# exe = EXE(...) define las propiedades del archivo .exe final.
#
# name: El nombre del archivo ejecutable.
# icon: La ruta al icono de la ventana de la aplicación.
# console=False: Compila una aplicación sin la ventana de la consola (windowed).

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MdTab',  # Cambia 'MiAplicacion' al nombre deseado
    debug=False,
    # bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # <--- Esto crea una aplicación "windowed" sin consola.
    # disable_windowed_traceback=False,
    # argv_emulation=False,
    # target_arch=None,
    # codesign_identity=None,
    # entitlements_file=None,
    append_pkg=True,
    icon='icons/icon.png', # <--- Ruta a tu archivo de icono.
    version='version.txt' # <--- Esto indica a PyInstaller que lea la información
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    # upx_exclude=[],
    name='Markdown Tab' # Nombre de la carpeta de salida
)