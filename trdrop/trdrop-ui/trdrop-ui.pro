# ----------------
# qt configuration
# ----------------
QT += qml quick

# ----------------
# project configuration
# ----------------
TEMPLATE = app
CONFIG += c++14

# ----------------
# filepaths
# ----------------
INCLUDEPATH += source

SOURCES += \
        source/main.cpp

RESOURCES += views.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH = $$PWD
