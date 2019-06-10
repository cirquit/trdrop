import QtQuick 2.12
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import Trdrop 1.0

ImageViewerQML {
    id: imageviewer
    anchors.centerIn: parent
    //anchors.fill: parent
    //allowPainting: true

    Connections {
        target: imagecomposer
        onImageReady: {
            imageviewer.setImage(composed_image)
        }
        onResizeTriggered: {
            imageviewer.resize(size)
        }
    }
    Connections {
        target: imageviewer
        onDoneRendering: {
//              wrapper.grabToImage(function(result) {
//                                         result.saveToFile("blub.png");
//                                     });
            videocapturelist.readNextFrames()
        }
    }
}
