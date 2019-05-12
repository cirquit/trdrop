import QtQuick 2.12

Item {
    id: startupBackground
    width: parent.width
    height: parent.height

    // content background
    Rectangle {
        visible: true
        width: parent.width
        height: parent.height
        color: "#333333"
    }

    // content text
    Text {
        text: "<b>Ctrl + F</b> to add files<br>
               <b>Ctrl + E</b> to export<br>
               <b>Ctrl + O</b> for Options"
        font.family: "Helvetica"
        font.pointSize: 24
        color: "#878787"
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
    }

}
