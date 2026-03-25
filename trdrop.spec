# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for TRDrop single-file EXE."""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Only collect numba runtime submodules, skip tests/cuda tests
_numba_runtime = [
    m for m in collect_submodules("numba")
    if not m.startswith("numba.tests.")
    and not m.startswith("numba.cuda.tests.")
]

hiddenimports = (
    _numba_runtime
    + collect_submodules("av")
    + [
        "PyQt6.sip",
    ]
)

# numba needs its bundled data, but skip test data
datas = [
    (src, dst) for src, dst in collect_data_files("numba")
    if "tests" not in src
]

a = Analysis(
    ["src/trdrop/main.py"],
    pathex=[],
    hiddenimports=hiddenimports,
    datas=datas + [
        ("trdrop.ico", "."),
        ("trdrop_mac.png", "."),
    ],
    hookspath=[],
    runtime_hooks=["rthook_av.py"],
    excludes=[
        "numba.tests",
        "numba.cuda.tests",
        # Unused PyQt6 modules -- only QtCore/QtGui/QtWidgets are used
        "PyQt6.QtPdf",
        "PyQt6.QtSvg",
        "PyQt6.QtNetwork",
        "PyQt6.QtOpenGL",
        "PyQt6.QtDBus",
        "PyQt6.QtQml",
        "PyQt6.QtQuick",
        "PyQt6.QtBluetooth",
        "PyQt6.QtMultimedia",
        "PyQt6.QtWebEngine",
        "PyQt6.QtWebSockets",
        "PyQt6.QtPositioning",
        "PyQt6.QtSensors",
        "PyQt6.QtSerialPort",
        "PyQt6.QtSql",
        "PyQt6.QtTest",
        "PyQt6.QtXml",
    ],
)

# --- Strip unnecessary Qt/native binaries ---
_exclude_binaries = {
    # Qt software OpenGL fallback (7.3 MB) - all modern Windows have GPU drivers
    "opengl32sw.dll",
    # Qt PDF module (2.7 MB) - not used
    "Qt6Pdf.dll",
    # Qt Network (not used)
    "Qt6Network.dll",
    # Qt SVG (not used)
    "Qt6Svg.dll",
}

# av.libs encoders: can't exclude any -- avcodec links against all of them
_exclude_prefixes = ()

# Qt plugins not needed for this app
_exclude_qt_plugins = {
    "qtuiotouchplugin.dll",   # touch input
    "qsvgicon.dll",           # SVG icon engine
    "qpdf.dll",               # PDF image format
    "qsvg.dll",               # SVG image format
    "qtga.dll",               # TGA image format
    "qwbmp.dll",              # WBMP image format
    "qwebp.dll",              # WebP image format
    "qtiff.dll",              # TIFF image format
    "qicns.dll",              # Apple ICNS format
    "qminimal.dll",           # headless platform
    "qoffscreen.dll",         # offscreen platform
}

# Qt translation files (~1 MB)
a.binaries = [
    b for b in a.binaries
    if b[0].split("\\")[-1] not in _exclude_binaries
    and b[0].split("/")[-1] not in _exclude_binaries
    and b[0].split("\\")[-1] not in _exclude_qt_plugins
    and b[0].split("/")[-1] not in _exclude_qt_plugins
    and not b[0].endswith(".qm")
    and not any(b[0].split("\\")[-1].startswith(p) or b[0].split("/")[-1].startswith(p) for p in _exclude_prefixes)
]

a.datas = [
    d for d in a.datas
    if not d[0].endswith(".qm")
]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="TRDrop",
    icon="trdrop.ico",
    console=False,
    windowed=True,
)
