import QtQuick 2.0
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

ListView {
    id: listView
    anchors.fill: parent
    model: fileItemModel

    delegate: Item {
        implicitHeight: text.height
        width: listView.width
        RowLayout {
            id: text
            Text {
                text: "Name: " + model.name
                color: "#FFFFFF"
            }
            Text {
                text: "Container: " + model.container
                color: "#FFFFFF"
            }
            Text {
                text: "Position: " + model.position
                color: "#FFFFFF"
            }
            Text {
                text: "Index: " + index
                color: "#FFFFFF"
            }
            Button {
                text: "Click me!"
                enabled: {
                    if (index === 0)      { return true; }
                    else if (index === 1) { return fileItemModel.isFileSelected(0); }
                    else if (index === 2) { return fileItemModel.isFileSelected(0)
                                                && fileItemModel.isFileSelected(1); }
                    else return false;
                }
                onClicked: {
//                    if (index === 0)      { console.log("index: 0 - " + fileItemModel.isFileSelected(0)); }
//                    else if (index === 1) { console.log("index 1 - " + fileItemModel.isFileSelected(0)); }
//                    else if (index === 2) { console.log("index 2 - " + fileItemModel.isFileSelected(0)
//                                                + " " + fileItemModel.isFileSelected(1)); }
                    model.name = "Hello!";
                    model.fileSelected = true;
                    fileItemModel.resetModel();
                }
            }
            Button {
                text: "Remove it!"
                onClicked: {
                    fileItemModel.remove(index);
                    fileItemModel.appendDefaultFileItem();
                }
            }
        }
    }
}
