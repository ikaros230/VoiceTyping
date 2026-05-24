# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for VoiceTyping Windows build."""

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

project_root = Path(SPECPATH)

datas = collect_data_files("opencc")

hiddenimports = [
    "faster_whisper",
    "onnxruntime",
    "ctranslate2",
    "tokenizers",
    "huggingface_hub",
    "pystray._win32",
    "PIL._tkinter_finder",
    "pydantic",
    "sounddevice",
    "scipy.io.wavfile",
]
hiddenimports += collect_submodules("faster_whisper")

a = Analysis(
    [str(project_root / "src" / "voicetyping" / "__main__.py")],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["matplotlib", "pandas", "pytest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VoiceTyping",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "assets" / "icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="VoiceTyping",
)
