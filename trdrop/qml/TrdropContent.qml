import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Controls 2.12
import QtMultimedia 5.12
import Trdrop 1.0

Item {
    id: renderer
    anchors.centerIn: parent
    anchors.fill: parent

    Connections {
        target: imagecomposer
        onImageReady: { imageviewer.setImage(composed_image) }
        onResizeTriggered: {
            imageviewer.resize(size);
            //fpsTextExportView.cellWidth = size.width / fpsTextExportView.video_count
            //fpsTextExportView.cellHeight = size.height / 5
        }
    }
    Connections {
        target: imageviewer
        onDoneRendering: {
            videocapturelist.readNextFrames()
        }
    }

    Connections {
        target: fpsOptionsModel
        onPropagateFPSOptions: {
            imageviewer.setFPSOptions(fpsOptionsList);
        }
    }

    Connections {
        target: exportController
        onStartExporting: {
            imageviewer.setEmitRenderingSignal(true);
        }
        onStopExporting: {
            imageviewer.setEmitRenderingSignal(false);
        }
    }

    ImageViewerQML {
        id: imageviewer
        anchors.centerIn: parent
    }
}
