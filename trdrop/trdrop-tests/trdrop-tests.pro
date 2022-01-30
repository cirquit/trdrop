# ----------------
# qt configuration
# ----------------
QT += testlib
QT -= gui

# ----------------
# project configuration
# ----------------
TARGET = trdrop-tests
TEMPLATE = app
CONFIG += c++14 console
CONFIG -= app_bundle
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

LIBS += -L$$PWD/../../build/$$DESTINATION_PATH -ltrdrop-lib

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

INCLUDEPATH += source \
    ../trdrop-lib/source

SOURCES += \
    source/ffmpeg_tests.cpp \
    source/main.cpp \
    source/test_suite.cpp

# HEADERS +=
!build_pass:message(trdrop-tests dir: $${PWD})

HEADERS += \
    source/ffmpeg_tests.h \
    source/test_suite.h
