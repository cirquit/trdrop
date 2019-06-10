import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2

import "../utils.js" as Utils

Window {
    id: exportWindow
    title: "Export"
    visible: true
    width: 800
    height: 600
    flags: Qt.SubWindow
    Material.theme: Material.Dark
    Material.accent: Material.DeepPurple
    Pane {
        width: parent.width
        height: parent.height
        GridLayout {
            columns: 3
            rows: 4
            Layout.margins: 10
            Layout.minimumHeight: 600
            Layout.minimumWidth: 600
            Label {
                text: "Export to directory:"
            }

            Rectangle {
                border {
                    color: "#8066b0"
                    width: 1
                }
                Layout.fillWidth: parent
                height: 25
                width: 300
                Layout.leftMargin: 20
                Layout.rightMargin: 20
                color: "transparent"
                TextInput {
                    id: exportDirectoryLabel
                    anchors.fill: parent
                    leftPadding: 5
                    topPadding: 2
                    bottomPadding: 2
                    text: fileItemModel.getDefaultMoviesDirectory()
                    clip: true
                    font.pointSize: 12
                    color: "#FFFFFF"
                    onEditingFinished: {
                        exportDirectoryLabel.text = text;
                    }
               }
            }
            Button {
                text: "Browse"
                action: Action {
                    onTriggered: browseDirDialog.open()
                }
            }
            FileDialog {
                id: browseDirDialog
                title: "Please choose a directory"
                visible: false
                folder: shortcuts.movies
                selectFolder: true
                onAccepted: {
                    var qtFilePath = browseDirDialog.fileUrl.toString();
                    var realFilePath = Utils.urlToPath(browseDirDialog.fileUrl.toString())
                    exportDirectoryLabel.text = realFilePath;
                }
            }

            Label {
                text: "Resolution:"
            }
            ComboBox {
                Layout.leftMargin: 20
                Layout.rightMargin: 20
                Layout.fillWidth: true
                textRole: "resolutionName"
                model: resolutionsModel
                onActivated: {
                    let size = resolutionsModel.getSizeAt(currentIndex);
                    imagecomposer.resizeComposition(size);
                }
            }

            ProgressBar {
                id: exportProgressBar
                Layout.columnSpan: 3
                Layout.fillWidth: true
                value: 0.0
            }

            Button {
                id: exportButton
                Layout.columnSpan: 3
                Layout.fillWidth: true
                text: "Export"
                onClicked: {
                    // if running, stop and show Export again TODO
                    videocapturelist.readNextFrames()
                }
            }

            Connections {
                target: videocapturelist
                onFramesReady: {
                    exportProgressBar.value = videocapturelist.getVideoProgress(0);
                    exportButton.text       = Utils.round(videocapturelist.getVideoProgress(0) * 100, 1) + "%";
                }
                onFinishedProcessing: {
                    exportButton.text = "Export";
                    exportProgressBar.value = 0.0;
                }
            }

        }
    }
}
