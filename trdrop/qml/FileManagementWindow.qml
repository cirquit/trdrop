import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2

Window {
    id: fileManagementWindow
    title: "Manage Files"
    visible: true
    width: 800
    height: 400
    flags: Qt.SubWindow
    Material.theme: Material.Dark
    Material.accent: Material.DeepPurple

    Pane {
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
                onPressAndHold: held = true && edit.fileSelected
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
                    height: fileInformation.implicitHeight + 4
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
                        nameFilters: ["Video files (*.mp4 *.avi *.raw)"]
                        visible: false
                        folder: shortcuts.movies
                        onAccepted: {
                            fileItemList.openFile(index, fileDialog.fileUrl.toString())
                            // edit.name = fileDialog.fileUrl.toString();
                            edit.fileSelected = true;
                            fileItemList.get(index).name = fileDialog.fileUrl.toString();
                            // run stuff
                            // update
                        }
                    }
                    // file description, browse and remove buttons
                    RowLayout {
                        Layout.fillWidth: true
                        Column {
                            id: fileInformation
                            // center the browse button if no file was loaded
                            Layout.minimumWidth: edit.fileSelected ? fileManagementWindow.width * 0.78
                                                                   : fileManagementWindow.width * 0.50 - browseButton.width * 0.5
                            padding: 7
                            Layout.fillWidth: true

                            Label { font.pixelSize: 17; text:  edit.fileSelected ? "Filename:  " + edit.name : " " }
                            Label { font.pixelSize: 17; text:  edit.fileSelected ? "Size: " + edit.sizeMB + " MB" : " " }
                            Label { font.pixelSize: 17; text:  edit.fileSelected ? "Container: " + edit.container : " "  }
                            Label { font.pixelSize: 17; text:  edit.fileSelected ? "Video Index: " + fileDragArea.DelegateModel.itemsIndex : " " }
                        }
                        Button {
                            id: browseButton
                            // only allow additional files if the previous slots were filled
                            enabled: {
                                if (index === 0) { return true; }
                                else if (index === 1) { return fileItemList.get(0).fileSelected; }
                                else if (index === 2) { return fileItemList.get(0).fileSelected
                                                            && fileItemList.get(1).fileSelected; }
                            }
                            hoverEnabled: true
                            Layout.fillHeight: true
                            flat: true
                            // change icon if no file was loaded yet
                            icon.source: edit.fileSelected ? "qrc:/images/browse-icon.png" : "qrc:/images/add-icon.png"
                            ToolTip.text: "Browse"
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            onClicked: {
                                fileDialog.open()
                                //console.log(fileItemList.get(0).fileSelected)
//                                console.log("fileItemList: " + fileItemList)
//                                console.log("get: " + fileItemList.get(index))
//                                console.log("fileItemList.model.data: " + fileItemList.model.data(0))
//                                console.log("model.items: " + model.items(0))
//                                console.log("model.data: " + model.data(0))
                            }
                        }
                        Button {
                            id: removeButton
                            // show this button if a file was loaded
                            visible:  edit.fileSelected
                            hoverEnabled: true
                            Layout.fillHeight: true
                            flat: true
                            icon.source: "qrc:/images/remove-icon.png"
                            ToolTip.text: "Remove"
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            onClicked: {
                                fileItemList.removeItem(index)
                                fileItemList.addDefaultFileItem()
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
                        var fromItem  = fileItemList.model.data(fromIndex)
                        var toItem    = fileItemList.model.data(toIndex)
                        if (fromItem.fileSelected && toItem.fileSelected)
                        {
                            visualModel.items.move(fromIndex, toIndex)
                        }
                    }
                }
            }
        }

        ListView {
            id: fileView
            anchors { fill: parent; margins: 2 }
            spacing: 4
            model: DelegateModel {
                id: visualModel
                model: fileItemList.model
                delegate: fileDragDelegate
            }
        }
    }


}
