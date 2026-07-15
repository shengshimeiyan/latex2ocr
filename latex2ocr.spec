# -*- mode: python ; coding: utf-8 -*-
import os

BASE_DIR = os.path.abspath('.')

a = Analysis(
    ['main_v108.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(BASE_DIR, 'mathjax'), 'mathjax'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'tkinter', '_tkinter', 'PyQt4', 'PySide2',
        'scipy', 'numpy', 'pandas', 'IPython', 'notebook',
        'pyautogui', 'psutil', 'pygetwindow',
        'PyQt5.QtQuick', 'PyQt5.QtQml', 'PyQt5.QtQuickWidgets',
        'PyQt5.QtPositioning', 'PyQt5.QtMultimedia',
        'PyQt5.QtSql', 'PyQt5.QtXml', 'PyQt5.QtSvg',
        'PyQt5.QtBluetooth', 'PyQt5.QtDBus',
        'unittest', 'pydoc', 'doctest',
        'rich', 'pygments',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='latex2ocr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
