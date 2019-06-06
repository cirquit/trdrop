import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2

// import "../utils.js" as Utils

Window {
    id: exportWindow
    title: "Export"
    visible: true
    width: 800
    height: 400
    flags: Qt.SubWindow
    Material.theme: Material.Dark
    Material.accent: Material.DeepPurple
    Pane {
        width: parent.width
        height: parent.height
        Label {
            text: "Exporting stuff..."
        }
    }
}
