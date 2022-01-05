# ----------------
# qt configuration
# ----------------
QT -= gui

# ----------------
# project configuration
# ----------------
TARGET = trdrop-lib
TEMPLATE = lib
DEFINES += TRDROPLIB_LIBRARY
CONFIG += c++14

# ----------------
# filepaths
# ----------------
INCLUDEPATH += source

SOURCES += \
    source/models/trdrop_lib.cpp

HEADERS += \
    source/trdrop-lib_global.h \
    source/models/trdrop_lib.h
