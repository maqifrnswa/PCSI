# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['pcsiGUI.py'],
             pathex=['/home/showard/compressedsensing/PCSI'],
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
          a.binaries,
          a.zipfiles,
          a.datas - [('/usr/lib/x86_64-linux-gnu/qt5/qt.conf', '/usr/lib/x86_64-linux-gnu/qt5/qt.conf', 'DATA')],
          [],
          name='pcsiGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
