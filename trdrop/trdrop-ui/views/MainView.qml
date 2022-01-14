import QtQuick 2.12
import QtQuick.Window 2.12

Window {
    // Min. Resolution: 1280x720 (720p)
    // Max. Resolution: 3840x2160 (4k)
    width: 1280
    height: 720
    visible: true
    title: qsTr("trdrop")
    // set to Qt.Dialog for Linux development purposes, should be changed on release to Qt.Window
    // TODO check for implications on Windows
    flags: Qt.Dialog

    Text {
        text: masterController.ui_welcomeMessage
    }
}
