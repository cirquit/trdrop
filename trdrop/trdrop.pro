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

windows: INCLUDEPATH += c:\opencv-4.1.0-64\build\install\include
windows: LIBS += -LC:\\opencv-4.1.0-64\build\install\x64\mingw\lib \
        -lopencv_calib3d410 \
        -lopencv_core410 \
        -lopencv_dnn410 \
        -lopencv_features2d410 \
        -lopencv_flann410 \
        -lopencv_gapi410 \
        -lopencv_highgui410 \
        -lopencv_imgcodecs410 \
        -lopencv_imgproc410 \
        -lopencv_ml410 \
        -lopencv_objdetect410 \
        -lopencv_photo410 \
        -lopencv_stitching410 \
        -lopencv_videoio410 \
        -lopencv_video410


# openmp support to allow parallelism
LIBS += -fopenmp
QMAKE_CXXFLAGS += -fopenmp


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
    headers/cpp_interface/checkboxitem.h \
    headers/cpp_interface/fileitem.h \
    headers/cpp_interface/resolution.h \
    headers/cpp_interface/valueitem.h \
    headers/cpp_interface/colorpickitem.h \
    headers/cpp_interface/tearoptions.h \
    headers/cpp_interface/textedititem.h \
    headers/cpp_interface/videocapturelist.h \
    headers/cpp_interface/imageformat.h \
    headers/cpp_interface/videoformat.h \
    headers/cpp_interface/frameratemodel.h \
    headers/qml_interface/imagecomposer_qml.h \
    headers/qml_interface/imageconverter_qml.h \
    headers/qml_interface/renderer_qml.h \
    headers/qml_interface/videocapturelist_qml.h \
    headers/qml_interface/viewer_qml.h \
    headers/qml_interface/exporter_qml.h \
    headers/qml_models/fileitemmodel.h \
    headers/qml_models/generaloptionsmodel.h \
    headers/qml_models/resolutionsmodel.h \
    headers/qml_models/tearoptionsmodel.h \
    headers/qml_models/imageformatmodel.h \
    headers/qml_models/videoformatmodel.h \
    headers/qml_models/exportoptionsmodel.h \
    headers/cpp_interface/framerateplot.h \
    headers/cpp_interface/frametimeplot.h \
    headers/cpp_interface/frametimemodel.h \
    headers/cpp_interface/frameprocessing.h \
    headers/qml_interface/frameprocessing_qml.h \
    headers/cpp_interface/teardata.h \
    headers/cpp_interface/tearmodel.h \
    headers/cpp_interface/framerateoptions.h \
    headers/qml_models/framerateoptionsmodel.h


RC_ICONS = images/trdrop_logo_alpha.ico
