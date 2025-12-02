# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
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
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MdTab',
    icon='icons/icon.png',
    version='version.txt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Markdown Tab',
)
