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
    width: 740
    height: 390
    flags: Qt.SubWindow
    Material.theme: Material.Dark
    Material.accent: Material.DeepPurple
    Pane {
        width: parent.width
        height: parent.height

        ListView {
            id: exportOptionsView
            anchors { fill: parent; margins: 10 }
            Layout.minimumHeight: 600
            Layout.minimumWidth: 600
            model: DelegateModel {
                id: exportOptionsVisual
                model: exportOptionsModel
                delegate: exportOptionsDelegate
            }
        }
        Component {
            id: exportOptionsDelegate
            GridLayout {
                columns: 3
                rows: 7

                Label {
                    Layout.leftMargin: 54
                    text: model.exportDirectoryName
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
                        text: model.exportDirectoryValue
                        clip: true
                        font.pointSize: 12
                        color: "#FFFFFF"
                        onEditingFinished: {
                            model.exportDirectoryValue = text;
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
                        model.exportDirectoryValue = realFilePath;
                    }
                }


                Switch {
                    id: exportAsImageSequenceSwitch
                    text: model.imagesequencePrefixName
                    checked: model.imagesequencePrefixEnabled
                    action: Action {
                        onTriggered: {
                            model.imagesequencePrefixEnabled = !checked;
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
                        enabled: model.imagesequencePrefixEnabled
                        text: model.imagesequencePrefixValue
                        clip: true
                        font.pointSize: 12
                        color: enabled ? "#FFFFFF" : "#b0b0b0";
                        onEditingFinished: {
                            model.imagesequencePrefixValue = text;
                        }
                    }
                }
                ComboBox {
                    Layout.fillWidth: true
                    textRole: "imageFormatName"
                    model: imageFormatModel
                    //enabled: model.imagesequencePrefixEnabled
                    onActivated: {
                        //let format = imageFormatModel.getValueAt(currentIndex);
                        imageFormatModel.setActiveValueAt(currentIndex);

                        //imagecomposer.resizeComposition(size);
                    }
                }


//                Switch {
//                    id: exportAsVideoSwitch
//                    text: model.videoPrefixName
//                    checked: model.videoPrefixEnabled
//                    action: Action {
//                        onTriggered: {
//                            model.videoPrefixEnabled = !checked;
//                        }
//                    }
//                }
//                Rectangle {
//                    border {
//                        color: "#8066b0"
//                        width: 1
//                    }
//                    Layout.fillWidth: parent
//                    height: 25
//                    width: 300
//                    Layout.leftMargin: 20
//                    Layout.rightMargin: 20
//                    color: "transparent"
//                    TextInput {
//                        id: exportAsVideoName
//                        anchors.fill: parent
//                        leftPadding: 5
//                        topPadding: 2
//                        bottomPadding: 2
//                        enabled: model.videoPrefixEnabled
//                        text: model.videoPrefixValue
//                        clip: true
//                        font.pointSize: 12
//                        color: enabled ? "#FFFFFF" : "#b0b0b0";
//                        onEditingFinished: {
//                            model.videoPrefixValue = text;
//                        }
//                    }
//                }
//                ComboBox {
//                    id: exportAsVideoNameEnding
//                    Layout.fillWidth: true
//                    textRole: "videoFormatName"
//                    enabled: false
//                    model: videoFormatModel
//                    onActivated: {
//                        let format = videoFormatModel.getValueAt(currentIndex);
//                        //console.log(format)
//                        //let size = resolutionsModel.getSizeAt(currentIndex);
//                        //imagecomposer.resizeComposition(size);
//                    }
//                }


                Switch {
                    id: enableLivePreviewSwitch
                    text: model.enableLivePreviewName
                    checked: model.enableLivePreviewValue
                    action: Action {
                        onTriggered: {
                            model.enableLivePreviewValue = !model.enableLivePreviewValue;
                            checked: model.enableLivePreviewValue
                        }
                    }
                }
                Label {
                    Layout.columnSpan: 2
                }


                Switch {
                    id: exportAsOverlaySwitch
                    text: model.exportAsOverlayName
                    checked: model.exportAsOverlayValue
                    action: Action {
                        onTriggered: {
                            model.exportAsOverlayValue = !model.exportAsOverlayValue;
                            checked: model.exportAsOverlayValue
                        }
                    }
                }
                Label {
                    Layout.columnSpan: 2
                }


                Label {
                    Layout.leftMargin: 54
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
                Label { }

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
                    enabled: model.exportButtonEnabled
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
                        exportProgressBar.value = videocapturelist.getShortestVideoProgress();
                        exportButton.text       = Utils.round(videocapturelist.getShortestVideoProgress() * 100, 1) + "%";
                    }
                    onFinishedProcessing: {
                        exportButton.text = "Export";
                        exportProgressBar.value = 0.0;
                    }
                }

            }
        }
     }
}