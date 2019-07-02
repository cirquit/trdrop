import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import Trdrop 1.0

Item {
    id: trdropcontent
    anchors.centerIn: parent
    anchors.fill: parent

    Connections {
        target: exporter
        onImageReady: { viewer.setImage(image) }
    }

    Connections {
        target: viewer
        onRequestNextImages: {
            if (exporter.isExporting()){
                videocapturelist.readNextFrames()
            }
        }
    }

    ViewerQML {
        id: viewer
        anchors.centerIn: parent
    }
}
