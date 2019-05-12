import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Window 2.12

MenuBar
{
    Material.theme: Material.Dark
    Material.accent: Material.Purple

    Menu
    {
        title: qsTr("File")
        MenuItem
        {
            text: qsTr("Add files       Ctrl+F")
            action: Action {
                shortcut: "Ctrl+F"
                onTriggered: {
                    var component = Qt.createComponent("FileManagementWindow.qml");
                    var win = component.createObject(rootWindow);
                    win.show();
                }
            }
        }
        MenuSeparator { }
        MenuItem
        {
            //shortcut: "Ctrl+E"
            text: qsTr("Export")
            onTriggered: console.log("Export onTriggered");
        }
        MenuSeparator { }
        MenuItem
        {
            text: qsTr("Exit")
            onTriggered: Qt.quit();
        }
    }
    Menu
    {
        title: qsTr("Tools")
        MenuItem
        {
            text: qsTr("Options       Ctrl+O")
            action: Action {
                shortcut: "Ctrl+O"
                onTriggered: {
                    var component = Qt.createComponent("OptionsWindow.qml");
                    var win = component.createObject(rootWindow);
                    win.show();
                }
            }
        }
    }
    Menu
    {
        title: qsTr("About")
        MenuItem
        {
            text: qsTr("About trdrop")
            onTriggered: console.log("About trdrop onTriggered")
        }
    }
}
