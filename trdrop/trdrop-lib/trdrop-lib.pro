QT -= gui

TARGET = trdrop-lib
TEMPLATE = lib
DEFINES += TRDROPLIB_LIBRARY
CONFIG += c++14

INCLUDEPATH += source

SOURCES += \
    source/models/trdrop_lib.cpp

HEADERS += \
    source/trdrop-lib_global.h \
    source/models/trdrop_lib.h
