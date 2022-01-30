# ----------------
# qt configuration
# ----------------
QT += qml quick

# ----------------
# project configuration
# ----------------
TEMPLATE = app
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

LIBS += -L$$PWD/../../build/$$DESTINATION_PATH -ltrdrop-lib

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


!build_pass:message(trdrop-ui dir: $${PWD})

INCLUDEPATH += source \
    ../trdrop-lib/source
SOURCES += \
        source/main.cpp

RESOURCES += views.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH = $$PWD
