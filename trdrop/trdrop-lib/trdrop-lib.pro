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
CONFIG += c++14 force_debug_info
include(../qmake-target-platform.pri)
include(../qmake-destination-path.pri)
# ----------------
# filepaths
# ----------------
DESTDIR = $$PWD/../../build/$$DESTINATION_PATH
OBJECTS_DIR = $$PWD/build/$$DESTINATION_PATH/.obj
MOC_DIR = $$PWD/build/$$DESTINATION_PATH/.moc
RCC_DIR = $$PWD/build/$$DESTINATION_PATH/.qrc
UI_DIR = $$PWD/build/$$DESTINATION_PATH/.ui

win32 {
    INCLUDEPATH += $(FFMPEG_SOURCE)\include
    LIBS += -L$(FFMPEG_SOURCE)\lib
}

unix {
    INCLUDEPATH += $(FFMPEG_SOURCE)/include
    LIBS += -L$(FFMPEG_SOURCE)/lib
}

!build_pass:message(trdrop-lib dir: $${PWD})

LIBS += -lavcodec \
    -lavdevice \
    -lavformat \
    -lavfilter \
    -lswresample \
    -lswscale \
    -lavutil \
    -lpostproc \
    -lz \
    -lm \
    -lgnutls \
    -lpthread \
    -lX11 \
    -lva \
    -lvdpau \
    -ldav1d \
    -lass \
    -lmp3lame \
    -lopus \
    -lx264 \
    -lx265 \
    -lvpx \
    -lvorbisenc \
    -lvorbis \
    -lfdk-aac \
    -lSvtAv1Enc \
    -lva-drm \
    -lva-x11

INCLUDEPATH += source

SOURCES += \
    source/controllers/mastercontroller.cpp \
    source/models/trdrop_lib.cpp \
    source/models/video.cpp

HEADERS += \
    source/controllers/mastercontroller.h \
    source/models/video.h \
    source/trdrop-lib_global.h \
    source/models/trdrop_lib.h
