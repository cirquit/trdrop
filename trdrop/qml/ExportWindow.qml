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
            rows: 8
            Layout.margins: 10
            Layout.minimumHeight: 600
            Layout.minimumWidth: 600
            Label {
                Layout.leftMargin: 53
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

            Switch {
                id: exportAsImageSequenceSwitch
//                Layout.columnSpan: 2
                text: "Export as image sequence"
                checked: true
                action: Action {
                    onTriggered: {
                        //model.enableViewValue = !model.enableViewValue;
                        //checked: model.enableViewValue
                    }
                }
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
                    id: exportAsImageSequenceSwitchName
                    anchors.fill: parent
                    leftPadding: 5
                    topPadding: 2
                    bottomPadding: 2
                    text: "exportsequence_"
                    clip: true
                    font.pointSize: 12
                    color: "#FFFFFF"
                    onEditingFinished: {
                        //exportDirectoryLabel.text = text;
                    }
               }
            }
            ComboBox {
                Layout.fillWidth: true
                //textRole: "resolutionName"
                model: [".jpg", ".png"]
                onActivated: {
                    //let size = resolutionsModel.getSizeAt(currentIndex);
                    //imagecomposer.resizeComposition(size);
                }
            }


            Switch {
                id: exportAsVideoSwitch
                text: "Export as video"
                checked: true
                action: Action {
                    onTriggered: {
                        //model.enableViewValue = !model.enableViewValue;
                        //checked: model.enableViewValue
                    }
                }
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
                    id: exportAsVideoName
                    anchors.fill: parent
                    leftPadding: 5
                    topPadding: 2
                    bottomPadding: 2
                    text: "videox_vs_videoy"
                    clip: true
                    font.pointSize: 12
                    color: "#FFFFFF"
                    onEditingFinished: {
                        //exportDirectoryLabel.text = text;
                    }
               }
            }
            ComboBox {
                Layout.fillWidth: true
                //textRole: "resolutionName"
                model: [".avi", ".mp4"]
                onActivated: {
                    //let size = resolutionsModel.getSizeAt(currentIndex);
                    //imagecomposer.resizeComposition(size);
                }
            }

            Switch {
                id: exportOverlay
//                Layout.columnSpan: 2
                text: "Export overlay only"
                checked: true
                action: Action {
                    onTriggered: {
                        //model.enableViewValue = !model.enableViewValue;
                        //checked: model.enableViewValue
                    }
                }
            }
            Label {
                Layout.columnSpan: 2
            }

            Switch {
                id: exportDelta
//                Layout.columnSpan: 2
                text: "Export image difference"
                checked: true
                action: Action {
                    onTriggered: {
                        //model.enableViewValue = !model.enableViewValue;
                        //checked: model.enableViewValue
                    }
                }
            }
            Label {
                Layout.columnSpan: 2
            }

            Label {
                Layout.leftMargin: 53
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
            Label {

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
                    if (exporter.isExporting())
                    {
                        exportButton.text = "Export";
                        exportProgressBar.value = 0.0;
                        exporter.stopExporting();
                    } else {
                        exporter.startExporting()
                    }
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
