# -*- mode: python ; coding: utf-8 -*-

import os

spec_root = os.path.abspath(SPECPATH)

block_cipher = None


a = Analysis(['pcsiGUI.py'],
             pathex=[spec_root],
             binaries=[],
             datas=[],
             hiddenimports=['packaging.requirements', 'pkg_resources.py2_warn', 'PIL', 'PIL._imagingtk', 'PIL._tkinter_finder','tkinter'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='pcsiGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas - [('/usr/lib/x86_64-linux-gnu/qt5/qt.conf', '/usr/lib/x86_64-linux-gnu/qt5/qt.conf', 'DATA')],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='pcsiGUI')
