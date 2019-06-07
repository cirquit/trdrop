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
            Label {
                id: exportDirectoryLabel
                text: "                                                 "
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
                Layout.columnSpan: 2
                Layout.fillWidth: true
                model: ListModel {
                       id: cbItems
                       ListElement { text: "1280 x 1080" }
                   }
                onCurrentIndexChanged: {
                    console.debug(cbItems.get(currentIndex).width + ", " + cbItems.get(currentIndex).height)
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
