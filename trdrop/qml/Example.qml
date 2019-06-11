import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2

import "../utils.js" as Utils

Item {
    id: something
    anchors.centerIn: parent
    anchors.fill: parent

    ListView {
        id: fpsExportView
        anchors { fill: parent; margins: 20 }
        model: DelegateModel {
            id: fpsExportVisual
            model: fpsOptionsModel
            delegate: fpsExportDelegate
        }
    }
    Component {
        id: fpsExportDelegate

        Label {
            x: 100 * model.index
            text: model.displayedText
            color: model.color
        }
    }
}
