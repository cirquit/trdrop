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

LIBS += -L$$PWD/../../build/$$DESTINATION_PATH -ltrdrop-lib

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
