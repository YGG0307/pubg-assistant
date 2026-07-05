# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置
用法: pyinstaller RuntimeBroker.spec
"""

import sys
from pathlib import Path

# 需要打包的额外数据文件夹
datas = []

# 模板图片
templates_dir = Path("templates")
if templates_dir.exists():
    datas.append((str(templates_dir), "templates"))

# Tesseract OCR（如果安装在本项目目录）
tesseract_dir = Path("Tesseract")
if tesseract_dir.exists():
    datas.append((str(tesseract_dir), "Tesseract"))

# 配置文件模板
if Path("config.json").exists():
    datas.append(("config.json", "."))

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "win32gui",
        "win32process",
        "win32api",
        "win32con",
        "win32event",
        "winerror",
        "pydirectinput",
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        "pytesseract",
        "cv2",
        "numpy",
        "PIL",
        "psutil",
        "requests",
        "pytweening",
        "wmi",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter.test",
        "unittest",
        "email",
        "http",
        "xmlrpc",
        "pydoc",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="微凉Pro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,          # UPX 压缩，减小体积
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # 不显示命令行窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,          # 可添加图标: icon="icon.ico"
)