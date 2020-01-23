# -*- mode: python -*-

block_cipher = None


a = Analysis(['hydra_main.py'],
             pathex=['/home/owiredu/Documents/MY PROGRAMMING PROJECTS/Python 3/HYDRA'],
             binaries=[],
             datas=[('/home/owiredu/Documents/MY PROGRAMMING PROJECTS/Python 3/HYDRA', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
	  a.binaries,
          a.zipfiles,
          a.datas,
          name='Hydra',
	  exclude_binaries=False,
          debug=False,
          strip=False,
          upx=True,
          console=False, icon='hydra_icon.png' )
