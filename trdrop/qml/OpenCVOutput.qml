import QtQuick 2.12
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import Trdrop 1.0

QMLImageViewer {
    id: imageviewer
    anchors.centerIn: parent
    Connections {
        target: converter
        // see imageReady Q_SIGNAL in converter.h
        onImageReady: {
            console.log("Got: On Image Ready Signal, triggering getNextFrame")
            imageviewer.setImage(image)
        }
    }
    Connections {
        target: imageviewer
        onDoneRendering: {
            console.log("Got: On Done Rendering Signal, triggering getNextFrame")
            capture.getNextFrame()
        }
    }
}
