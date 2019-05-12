import QtQuick 2.0
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

ListView {
    id: listView
    anchors.fill: parent
    model: fileItemList.model

    delegate: Item {
        implicitHeight: text.height
        width: listView.width
        RowLayout {
            id: text
            Text {
                text: "Name: " + edit.name
                color: "#FFFFFF"
            }
            Text {
                text: "Container: " + edit.container
                color: "#FFFFFF"
            }
            Text {
                text: "Position: " + edit.position
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
                    else if (index === 1) { return fileItemList.get(0).fileSelected; }
                    else if (index === 2) { return fileItemList.get(0).fileSelected
                                                && fileItemList.get(1).fileSelected; }
                }
                onClicked: {
                    edit.name = "Hello!"
                    edit.fileSelected = true;
                }
            }
        }
    }
}
