import QtQuick 2.12
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import Trdrop 1.0

QMLImageViewer {
    id: imageviewer
    anchors.centerIn: parent
    Connections {
        target: converter
        onImageReady: {
            //console.log(image)
            imageviewer.setImage(image)
        }
    }
}
