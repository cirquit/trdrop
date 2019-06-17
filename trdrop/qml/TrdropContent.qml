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
            fpsTextExportView.cellWidth = size.width / fpsTextExportView.video_count
            fpsTextExportView.cellHeight = size.height / 5
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
    Connections {
        target: fileItemModel
        onUpdateFileItemPaths: {
            fpsTextExportView.cellWidth = fpsTextExportView.width / filePaths.length
            fpsTextExportView.video_count = filePaths.length
        }
    }

    ImageViewerQML {
        id: imageviewer
        anchors.centerIn: parent
    }

    GridView {
        // this property is changed
        property int video_count: 1
        id: fpsTextExportView
        cellHeight: fpsTextExportView.height / 5
        cellWidth:  fpsTextExportView.width

        anchors { fill: imageviewer; }
        model: DelegateModel {
            model: fpsOptionsModel
            delegate: fpsTextExportDelegate
        }
    }

    Component {
        id: fpsTextExportDelegate
        Item {
            Label {
                x: 20
                y: 15
                text: model.displayedText + " 59.4"
                font: displayedTextFont
                color: model.color
                visible: model.displayedTextEnabled && model.fpsOptionsEnabled
            }
        }
    }
}
