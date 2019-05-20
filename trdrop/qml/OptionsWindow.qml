import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Controls 2.5
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2

Window {
    id: optionsWindow
    title: "Options"
    visible: true
    width: 800
    height: 800
    flags: Qt.SubWindow
    Material.theme: Material.Dark
    Material.accent: Material.DeepPurple

    Pane {
        width:  optionsWindow.width
        height: optionsWindow.height

        GridLayout {
            rows: 1
            columns: 2
            anchors.fill: parent
            GridLayout {
                rows: 4
                columns: 1
                Button {
                    id: generalTab
                    Layout.minimumWidth: 150
                    Layout.minimumHeight: 150
                    flat: true
                    text: "General"
                    font.pointSize: 15
                    highlighted: generalOptions.visible
                    onClicked: {
                        generalOptions.visible   = true
                        fpsOptions.visible       = false
                        tearOptions.visible      = false
                        frametimeOptions.visible = false
                    }
                }
                Button {
                    id: fpsTab
                    Layout.minimumWidth: 150
                    Layout.minimumHeight: 150
                    flat: true
                    text: "FPS"
                    font.pointSize: 15
                    highlighted: fpsOptions.visible
                    onClicked: {
                        generalOptions.visible   = false
                        fpsOptions.visible       = true
                        tearOptions.visible      = false
                        frametimeOptions.visible = false
                    }
                }
                Button {
                    id: tearTab
                    Layout.minimumWidth: 150
                    Layout.minimumHeight: 150
                    flat: true
                    text: "Tear"
                    font.pointSize: 15
                    highlighted: tearOptions.visible
                    onClicked: {
                        generalOptions.visible   = false
                        fpsOptions.visible       = false
                        tearOptions.visible      = true
                        frametimeOptions.visible = false
                    }
                }
                Button {
                    id: frametimeTab
                    Layout.minimumWidth: 150
                    Layout.minimumHeight: 150
                    flat: true
                    text: "Frametime"
                    font.pointSize: 15
                    highlighted: frametimeOptions.visible
                    onClicked: {
                        generalOptions.visible   = false
                        fpsOptions.visible       = false
                        tearOptions.visible      = false
                        frametimeOptions.visible = true
                    }
                }
            }
            Rectangle {
                id: generalOptions
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.margins: 5
                radius: 4
                border.width: 1
                border.color: "#bface3"
                color: "#404040"
                visible: true
                ListView {
                    id: generalOptionsView
                    anchors { fill: parent; margins: 20 }
                    spacing: 4
                    model: DelegateModel {
                        id: generalOptionsVisual
                        model: generalOptionsModel
                        delegate: generalOptionsDelegate
                    }
                }
                Component {
                    id: generalOptionsDelegate
                    GridLayout {
                        rows: 2
                        columns: 1
                        Switch {
                            text: model.enableViewName
                            checked: model.enableViewValue
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            ToolTip.text: model.enableViewTooltip
                            action: Action {
                                onTriggered: {
                                    model.enableViewValue = !model.enableViewValue;
                                    checked: model.enableViewValue
                                }
                            }
                        }
                        Button {
                            text: "Revert to default settings"
                            action: Action {
                                onTriggered: {
                                    fpsOptionsModel.revertModelToDefault();
                                    generalOptionsModel.revertModelToDefault();
                                }
                            }
                        }
                    }
                }
            }
            Rectangle {
                id: fpsOptions
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.margins: 5
                radius: 4
                border.width: 1
                border.color: "#bface3"
                color: "#404040"
                visible: false
                ListView {
                    id: fpsOptionsView
                    anchors { fill: parent; margins: 20 }
                    spacing: 4
                    model: DelegateModel {
                        id: fpsOptionsVisual
                        model: fpsOptionsModel
                        delegate: fpsOptionsDelegate
                    }
                }
                Component {
                    id: fpsOptionsDelegate
                    Frame {
                        width: fpsOptions.width * 0.95
                        GridLayout {
                            columns: 4

                            Label {
                                id: colorLabel
                                text: model.colorName + ":"
                                Layout.rightMargin: 5
                            }
                            Rectangle {
                                id: fpsColorRectangle
                                height: 20
                                color: model.color
                                border.color: "#8066b0"
                                border.width: 1
                                radius: 3
                                Layout.leftMargin:  50
                                Layout.rightMargin: 50
                                Layout.fillWidth: true
                                //ToolTip.text: model.colorTooltip
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: fpsColorDialog.open()
                                }
                                ColorDialog {
                                    id: fpsColorDialog
                                    title: "Please choose a color"
                                    onAccepted: {
                                        fpsColorRectangle.color = fpsColorDialog.color
                                        model.color = fpsColorDialog.color
                                    }
                                }
                            }
                            Button {
                                text:  "Replicate Color"
                                //ToolTip.text: "Replicate this color to tears and frametime of this video index"
                                //ToolTip.delay: 500
                                //ToolTip.visible: hovered
                                action: Action {
                                    onTriggered:
                                        tearOptionsModel.applyColor(model.color, index)
                                }
                            }
                            Label { }

                            Label {
                                text: model.pixelDifferenceName + ":"
                                Layout.rightMargin: 5
                                //ToolTip.text: model.pixelDifferenceTooltip
                                //ToolTip.delay: 500
                                //ToolTip.visible: hovered
                            }
                            SpinBox {
                                id: pixelDifferenceSpinBox
                                from: 0
                                to: 50
                                stepSize: 1
                                editable: true
                                value: model.pixelDifference
                                onValueChanged: if (model.pixelDifference !== value) model.pixelDifference = value;
                            }
                            Button {
                                text: "Apply to all videos"
                                action: Action {
                                    onTriggered: fpsOptionsModel.applyPixelDifference(model.pixelDifference)
                                }
                            }
                            Label { }

                            Label {
                                text: model.displayedTextName
                                //ToolTip.text: model.displayedTextTooltip
                                //ToolTip.delay: 500
                                //ToolTip.visible: hovered
                            }
                            Rectangle {
                                border {
                                    color: "#8066b0"
                                    width: 1
                                }
                                Layout.fillWidth: parent
                                height: 30
                                Layout.leftMargin: 20
                                Layout.rightMargin: 20
                                color: "transparent"
//                                ToolTip.text: model.displayedTextTooltip
//                                ToolTip.delay: 500
//                                ToolTip.visible: hovered
                                TextInput {
                                    id: fpsText
                                    anchors.fill: parent
                                    leftPadding: 5
                                    topPadding: 2
                                    bottomPadding: 2
                                    text: model.displayedText
                                    color: enabled ? model.color
                                                   : "#b0b0b0"
                                    clip: true
                                    font: model.displayedTextFont
                                    onEditingFinished: {
                                        model.displayedText = text;
                                    }
                                }
                            }
                            Button {
                                id: fpsTextCustomize
                                text: "Customize"
                                onClicked: {
                                    fontDialog.open()
                                }
                            }
                            FontDialog {
                                id: fontDialog
                                title: "Please choose a font"
                                font: Qt.font({ family: "Helvetica", pointSize: 15 })
                                onAccepted: {
                                    fpsText.font = fontDialog.font
                                    model.displayedTextFont = fontDialog.font
                                    console.log(model.displayedTextFont)
                                }
                            }
                            Switch {
                                id: fpsTextEnabled
                                checked: true
                                action: Action {
                                    onTriggered: {
                                        fpsText.enabled = !fpsText.enabled;
                                        fpsTextCustomize.enabled = !fpsTextCustomize.enabled;
                                        fpsTextEnabled.checked = fpsText.enabled
                                    }
                                }
                                //ToolTip.text: "Disable text and framerate rendering"
                                //ToolTip.delay: 500
                                //ToolTip.visible: hovered
                            }
                        }
                    }
                }
            }
            Rectangle {
                id: tearOptions
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.margins: 5
                radius: 4
                border.width: 1
                border.color: "#bface3"
                color: "#404040"
                visible: false
                ListView {
                    id: tearOptionsView
                    anchors { fill: parent; margins: 20 }
                    spacing: 4
                    model: DelegateModel {
                        id: tearOptionsVisual
                        model: tearOptionsModel
                        delegate: tearOptionsDelegate
                    }
                }
                Component {
                    id: tearOptionsDelegate
                    Frame {
                        width: tearOptions.width * 0.95
                        GridLayout {
                            columns: 3

                            Label {
                                text: model.enableTearsName
                            }
                            Switch {
                                Layout.columnSpan: 2
                                checked: model.enableTears
                                action: Action {
                                    onTriggered: {
                                        tearOptionsModel.setAllEnableTears(!model.enableTears)
                                    }
                                }
                            }

                            Label {
                                id: colorLabel
                                text: model.colorName + ":"
                                Layout.rightMargin: 5
                            }
                            Rectangle {
                                id: tearColorRectangle
                                height: 20
                                color: model.enableTears ? model.color : "#909090"
                                border.color: "#8066b0"
                                border.width: 1
                                radius: 3
                                Layout.leftMargin:  25
                                Layout.rightMargin: 25
                                ToolTip.text: model.colorTooltip
                                width: 70
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: tearColorDialog.open()
                                }
                                ColorDialog {
                                    id: tearColorDialog
                                    title: "Please choose a color"
                                    onAccepted: {
                                        model.color = tearColorDialog.color
                                    }
                                }
                            }
                            Button {
                                enabled: model.enableTears
                                text:  "Replicate Color"
                                action: Action {
                                    onTriggered:
                                        fpsOptionsModel.applyColor(model.color, index)
                                }
                            }
                        }
                    }
                }
            }
            Rectangle {
                id: frametimeOptions
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.margins: 5
                radius: 4
                border.width: 1
                border.color: "#bface3"
                color: "#404040"
                visible: false
            }
        }
    }
}
