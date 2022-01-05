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

# ----------------
# filepaths
# ----------------
INCLUDEPATH += source

SOURCES += \
    source/main.cpp

# HEADERS +=
