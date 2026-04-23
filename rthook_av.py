"""PyInstaller runtime hook: pre-load FFmpeg DLLs for av._core."""
import ctypes
import glob
import os
import sys

if hasattr(sys, "_MEIPASS"):
    av_libs = os.path.join(sys._MEIPASS, "av.libs")
    if os.path.isdir(av_libs):
        os.add_dll_directory(av_libs)
        os.environ["PATH"] = av_libs + os.pathsep + os.environ.get("PATH", "")

        # Load in dependency order: support libs -> avutil -> sw* -> avcodec -> rest
        _load_order = [
            "libgcc_s_seh-*.dll",
            "libwinpthread-*.dll",
            "libstdc++-*.dll",
            "zlib1-*.dll",
            "lib*.dll",
            "avutil-*.dll",
            "swresample-*.dll",
            "swscale-*.dll",
            "avcodec-*.dll",
            "avformat-*.dll",
            "avfilter-*.dll",
            "avdevice-*.dll",
        ]
        _loaded = set()
        for pattern in _load_order:
            for dll_path in glob.glob(os.path.join(av_libs, pattern)):
                if dll_path not in _loaded:
                    _loaded.add(dll_path)
                    try:
                        ctypes.CDLL(dll_path)
                    except OSError:
                        pass
