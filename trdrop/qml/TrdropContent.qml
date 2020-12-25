import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import Trdrop 1.0

Item {
    id: trdropcontent
    anchors.centerIn: parent
    anchors.fill: parent
    anchors.margins: 50

    // slightly convoluted, this should be reworked
    // the viewer can't take the exportOptionsModel as shared_ptr as its called from QML
    // and not from c++
    // we call the garbage collector to collect the sent images in JS
    Connections {
        target: exporter
        function onImageReady(image) { gc(); viewer.setImage(image, exportOptionsModel.enabledLivePreview()) }
    }

    Connections {
        target: viewer
        function onRequestNextImages() {
            if (exporter.isExporting()){
                videocapturelist.readNextFrames()
            }
        }
    }

    ViewerQML {
        id: viewer
        anchors.centerIn: parent
        anchors.fill: parent
    }
}
