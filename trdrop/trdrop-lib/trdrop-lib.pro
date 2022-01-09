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

win32 {
    INCLUDEPATH += $(FFMPEG_SOURCE)\include
    LIBS += -L$(FFMPEG_SOURCE)\lib
}

unix {
    INCLUDEPATH += $(FFMPEG_SOURCE)/include
    LIBS += -L$(FFMPEG_SOURCE)/lib
}

LIBS += -lavcodec \
    -lavdevice \
    -lavformat \
    -lavfilter \
    -lswresample \
    -lswscale \
    -lavutil \
    -lpostproc

INCLUDEPATH += source

SOURCES += \
    source/models/trdrop_lib.cpp

HEADERS += \
    source/models/ffmpeg_wrapper.h \
    source/trdrop-lib_global.h \
    source/models/trdrop_lib.h
