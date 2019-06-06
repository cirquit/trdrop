import QtQuick 2.12
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import Trdrop 1.0

QMLImageViewer {
    id: imageviewer
    anchors.centerIn: parent
    //allowPainting: true

    Connections {
        target: converter
        // see imagesReady Q_SIGNAL in converter.h
        onImagesReady: {
            console.log("Converter: Sending imagelist to imageviewer")
            imageviewer.setImages(qml_image_list)
        }
    }
    Connections {
        target: imageviewer
        onDoneRendering: {
            console.log("Imageviewer: Done rendering, calling getNextFrame to capture")
//              wrapper.grabToImage(function(result) {
//                                         result.saveToFile("blub.png");
//                                     });
            capture.readNextFrames()
        }
    }
}
