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
    source/controllers/mastercontroller.cpp \
    source/models/trdrop_lib.cpp

HEADERS += \
    source/controllers/mastercontroller.h \
    source/models/ffmpeg_wrapper.h \
    source/trdrop-lib_global.h \
    source/models/trdrop_lib.h
