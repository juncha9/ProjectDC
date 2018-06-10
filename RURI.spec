# -*- mode: python -*-

block_cipher = None

def get_pandas_path():
	import pandas
	pandas_path = pandas.__path__[0]
	return pandas_path

def get_pytagcloud_path():
	import pytagcloud
	pytagcloud_path = pytagcloud.__path__[0]
	return pytagcloud_path

def get_konlpy_path():
	import konlpy
	konlpy_path = konlpy.__path__[0]
	return konlpy_path


a = Analysis(['./src/RURI.py'],
             pathex=['./src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)

dict_tree = Tree(get_pytagcloud_path(), prefix='pytagcloud', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pytagcloud' not in x[0], a.binaries)

dict_tree = Tree(get_konlpy_path(), prefix='konlpy', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'konlpy' not in x[0], a.binaries)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Ruriweb Crawler',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
