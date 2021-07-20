import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2

import "../utils.js" as Utils

Window {
    id: fileManagementWindow
    title: "Manage Files"
    visible: true
    width: 800
    minimumHeight: 320
    flags: if (Qt.platform.os == "linux") { return Qt.SubWindow } else { return Qt.Dialog }
    Material.theme: Material.Dark
    Material.accent: Material.DeepPurple
    Pane {
        id: fileManagementPane
        width: parent.width
        height: parent.height
        Component {
            id: fileDragDelegate
            MouseArea {
                id: fileDragArea
                property bool held: false
                anchors { left: parent.left; right: parent.right }
                width: fileElement.width
                height: fileElement.height
                // pointer to the currently held item
                drag.target: held ? fileElement : undefined
                // scroll vertically
                drag.axis: Drag.YAxis
                // holding functionality, only allowed if a file is loaded
                onPressAndHold: held = true && model.fileSelected
                onReleased: held = false
                // ms
                pressAndHoldInterval: 10
                // file element, holding buttons and information about the loaded file and its interactions
                Rectangle {
                    id: fileElement
                    anchors {
                        horizontalCenter: parent.horizontalCenter
                        verticalCenter: parent.verticalCenter
                    }
                    width: fileDragArea.width;
                    height: fileInformation.implicitHeight
                    border.width: 1
                    border.color: fileDragArea.held ? "#bface3"
                                                    : "#8066b0"
                    Behavior on border.color { ColorAnimation { duration: 250 } }
                    color: fileDragArea.held ? "#aa7eb0"
                                             : "#545454"
                    Behavior on color { ColorAnimation { duration: 250 } }
                    // corner radius
                    radius: 2
                    // dragging parametrization
                    Drag.active: fileDragArea.held
                    Drag.source: fileDragArea
                    Drag.hotSpot.x: width / 2
                    Drag.hotSpot.y: height / 2
                    // dragging states
                    states: State {
                        when: fileDragArea.held
                        ParentChange { target: fileElement; parent: fileManagementWindow }
                        AnchorChanges {
                            target: fileElement
                            anchors { horizontalCenter: undefined; verticalCenter: undefined }
                        }
                    }
                    // browse directory with this dialog
                    FileDialog {
                        id: fileDialog
                        title: "Please choose an uncompressed video"
                        nameFilters: ["Video files (*.avi *.mp4 *.mov *.mkv *.raw)", "All files (*)"]
                        visible: false
                        folder: shortcuts.movies
                        onAccepted: {
                            var qtFilePath = fileDialog.fileUrl.toString();
                            var realFilePath = Utils.urlToPath(fileDialog.fileUrl.toString())
                            model.filePath = realFilePath;
                            model.qtFilePath = qtFilePath;
                            model.sizeMB = Utils.round(fileItemModel.getFileSize(realFilePath), 2)
                            model.fileSelected = true;
                            fileItemModel.emitFilePaths(getVisualFileItemPaths());
                            fileItemModel.resetModel();
                        }
                    }
                    // file description, browse and remove buttons
                    RowLayout {
                        Layout.fillWidth: true
                        Column {
                            id: fileInformation
                            // center the browse button if no file was loaded
                            Layout.minimumWidth: model.fileSelected ? fileManagementWindow.width * 0.78
                                                                    : fileManagementWindow.width * 0.50 - browseButton.width * 0.5
                            padding: 15
                            Layout.fillWidth: true
                            Label { font.pixelSize: 17; text:  model.fileSelected ? "Filepath:  "   + Utils.cutFilePath(model.filePath, 60) : " " }
                            Label { font.pixelSize: 17; text:  model.fileSelected ? "Size: "        + model.sizeMB + " MB" : " " }
                            Label { font.pixelSize: 17; text:  model.fileSelected ? "Recorded Framerate: "  + Utils.round(model.recordedFramerate, 2) + " FPS" : " " }
                        }
                        Button {
                            id: browseButton
                            // only allow additional files if the previous slots were filled
                            enabled: {
                                if      (index === 0) { return true; }
                                else if (index === 1) { return fileItemModel.isFileSelected(0); }
                                else if (index === 2) { return fileItemModel.isFileSelected(0)
                                                            && fileItemModel.isFileSelected(1); }
                                else return false;
                            }
                            hoverEnabled: true
                            Layout.fillHeight: true
                            flat: true
                            // change icon if no file was loaded yet
                            icon.source: model.fileSelected ? "qrc:/images/browse-icon.png"
                                                            : "qrc:/images/add-icon.png"
                            ToolTip.text: "Browse"
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            onClicked: fileDialog.open()
                        }
                        Button {
                            id: removeButton
                            visible:  model.fileSelected
                            hoverEnabled: true
                            Layout.fillHeight: true
                            flat: true
                            icon.source: "qrc:/images/remove-icon.png"
                            ToolTip.text: "Remove"
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            onClicked: {
                                fileItemModel.remove(index)
                                fileItemModel.appendDefaultFileItem()
                                fileItemModel.emitFilePaths(getVisualFileItemPaths());
                            }
                        }
                    }
                }
                DropArea {
                    anchors { fill: parent; margins: 10 }
                    // allow dragging if both items have files opened, determined if the name variable is set
                    onEntered: {
                        var fromIndex = drag.source.DelegateModel.itemsIndex;
                        var toIndex   = fileDragArea.DelegateModel.itemsIndex;
                        if (fileItemModel.isFileSelected(fromIndex) && fileItemModel.isFileSelected(toIndex))
                        {
                            visualModel.items.move(fromIndex, toIndex);
                        }
                    }
                    onExited: fileItemModel.emitFilePaths(getVisualFileItemPaths());
                }
            }
        }
        ListView {
            id: fileView
            anchors { fill: parent; margins: 2 }
            spacing: 4
            model: DelegateModel {
                id: visualModel
                model: fileItemModel
                delegate: fileDragDelegate
            }
            // animate when something is added
            add: Transition {
                SequentialAnimation {
                    // wait until remove has finished
                    PauseAnimation {
                        duration: 250
                    }
                    // blend in
                    NumberAnimation {
                        properties: "opacity"
                        from: 0.0
                        to: 1.0
                        duration: 1000
                        easing.type: Easing.Linear
                    }
                }
            }
            // animate when some gets removed
            remove: Transition {
                // blend out
                NumberAnimation {
                    properties: "opacity";
                    to: 0;
                    duration: 250;
                    easing.type: Easing.Linear
                }
            }
            // animate when entry is moved if another entry is deleted
            removeDisplaced: Transition {
                SequentialAnimation {
                    // wait until remove has finished
                    PauseAnimation {
                        duration: 250
                    }
                    NumberAnimation {
                        properties: "y";
                        duration: 500
                        easing.type: Easing.Linear
                    }
                }
            }
            // animate when entry is moved by hand
            displaced: Transition {
                NumberAnimation {
                    properties: "y"
                    duration: 250
                }
                from: "fromState"
                to: "toState"
            }
        }
    }

    Connections {
        target: fileItemModel
        function onUpdateFileItemPaths(filePaths) {
            videocapturelist.openAllPaths(filePaths);
            frameprocessing.resetState(videocapturelist.getUnsignedRecordedFramerates());
            fileItemModel.setRecordedFramerates(getVisualFileItemPaths()
                                               ,videocapturelist.getRecordedFramerates());
            framerateOptionsModel.updateEnabledRows(filePaths);
            tearOptionsModel.updateEnabledRows(filePaths);
            exportOptionsModel.setEnabledExportButton(filePaths.length > 0);
            videocapturelist.readNextFrames();
            if (filePaths.length === 0)
            {
                exporter.stopExporting();
            }
        }
    }

    //! We need to use the visual file items as the visualModel does not propate the shuffling to the underlying fileitemmodel
    function getVisualFileItemPaths()
    {
        var filepath_00 = visualModel.items.get(0).model.filePath;
        var filepath_01 = visualModel.items.get(1).model.filePath;
        var filepath_02 = visualModel.items.get(2).model.filePath;

        var filepath_list = [];

        if (filepath_00.length !== 0)
        {
            filepath_list.push(filepath_00);
        }
        if (filepath_01.length !== 0)
        {
            filepath_list.push(filepath_01);
        }
        if (filepath_02.length !== 0)
        {
            filepath_list.push(filepath_02);
        }

        return filepath_list;
    }

}
