QT += quick quickcontrols2 widgets multimedia
CONFIG += c++11

# The following define makes your compiler emit warnings if you use
# any Qt feature that has been marked deprecated (the exact warnings
# depend on your compiler). Refer to the documentation for the
# deprecated API to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

# OpenCV
unix: INCLUDEPATH += /usr/local/include/opencv4
unix: LIBS += -L/usr/local/lib \
        -lopencv_calib3d \
        -lopencv_core \
        -lopencv_dnn \
        -lopencv_features2d \
        -lopencv_flann \
        -lopencv_gapi \
        -lopencv_highgui \
        -lopencv_imgcodecs \
        -lopencv_imgproc \
        -lopencv_ml \
        -lopencv_objdetect \
        -lopencv_photo \
        -lopencv_stitching \
        -lopencv_videoio \
        -lopencv_video

SOURCES += \
        src/main.cpp

RESOURCES += qml.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

# Additional import path used to resolve QML modules just for Qt Quick Designer
QML_DESIGNER_IMPORT_PATH =

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target

HEADERS += \
    headers/fileitem.h \
    headers/fileitemmodel.h \
    headers/checkboxitem.h \
    headers/generaloptionsmodel.h \
    headers/fpsoptionsmodel.h \
    headers/colorpickitem.h \
    headers/valueitem.h \
    headers/fpsoptions.h \
    headers/textedititem.h \
    headers/tearoptions.h \
    headers/tearoptionsmodel.h \
    headers/customthread.h \
    headers/videocapturelist.h \
    headers/videocapturelist_qml.h \
    headers/imageconverter_qml.h \
    headers/imageviewer_qml.h \
    headers/imagecomposer_qml.h \
    headers/resolutionsmodel.h \
    headers/resolution.h
