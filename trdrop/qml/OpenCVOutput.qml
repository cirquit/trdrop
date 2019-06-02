import QtQuick 2.12
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import Trdrop 1.0

QMLImageViewer {
    id: imageviewer
    anchors.centerIn: parent
    Connections {
        target: converter
        // see imagesReady Q_SIGNAL in converter.h
        onImagesReady: {
            //console.log("Got " + qml_image_list.size() + " images")
            imageviewer.setImages(qml_image_list)
        }
    }
    Connections {
        target: imageviewer
        onDoneRendering: {
            //console.log("Got: On Done Rendering Signal, triggering getNextFrame")
            capture.readNextFrames()
        }
    }
}
