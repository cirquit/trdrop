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

INCLUDEPATH += source \
    ../trdrop-lib/source
SOURCES += \
        source/main.cpp

RESOURCES += views.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH = $$PWD
