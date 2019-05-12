import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.3

ListModel {
    ListElement {
        button_text: "Add Files"
        on_clicked: AddFilesDialog { }
        // onClicked: console.log("Added files")
    }
    ListElement {
        button_text: "Remove selected files"
        // onClicked: console.log("Remove selected files")
    }
}
