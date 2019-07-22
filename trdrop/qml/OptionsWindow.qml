import QtQuick 2.12
import QtQml.Models 2.1
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12
import QtQuick.Controls 2.5
import QtQuick.Controls.Styles 1.4
import QtQuick.Layouts 1.12
import QtQuick.Dialogs 1.2

import "../utils.js" as Utils

Window {
    id: optionsWindow
    title: "Options"
    visible: true
    width: 800
    height: 700
    flags: Qt.SubWindow || Qt.WindowSystemMenuHint
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
                        rows: 4
                        columns: 3
                        Switch {
                            text: model.enableFramerateName
                            checked: model.enableFramerateValue
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            ToolTip.text: model.enableFramerateTooltip
                            action: Action {
                                onTriggered: {
                                    model.enableFramerateValue = !model.enableFramerateValue;
                                    fpsTab.enabled = model.enableFramerateValue;
                                    framerateRange.enabled = model.enableFramerateValue;
                                    if (model.enableFramerateValue === false)
                                    {
                                        model.enableTearsValue = false;
                                        tearTab.enabled = false;
                                    }
                                }
                            }
                        }

                        Label {
                            Layout.leftMargin: 20
                            text: model.framerateRangeName
                        }
                        SpinBox {
                            id: framerateRange
                            from: 30
                            to: 180
                            stepSize: 10
                            editable: true
                            value: model.framerateRangeValue
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            ToolTip.text: model.framerateRangeTooltip
                            textFromValue: function(value, locale) { return value.toString() + ' frames'; }
                            valueFromText: function(value, locale) { return value.replace(' frames', ''); }
                            onValueChanged: {
                                if (model.framerateRangeValue !== value) model.framerateRangeValue = Utils.round(value, 0);
                            }
                        }
                        Switch {
                            Layout.columnSpan: 3
                            text: model.enableTearsName
                            checked: model.enableTearsValue
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            ToolTip.text: model.enableTearsTooltip
                            action: Action {
                                onTriggered: {
                                    model.enableTearsValue = !model.enableTearsValue;
                                    if (model.enableTearsValue) {
                                        fpsTab.enabled = true;
                                        tearTab.enabled = true;
                                        model.enableFramerateValue = true;
                                    } else {
                                        tearTab.enabled = false;
                                    }
                                }
                            }
                        }

                        Switch {
                            text: model.enableFrametimeName
                            checked: model.enableFrametimeValue
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            ToolTip.text: model.enableFrametimeTooltip
                            action: Action {
                                onTriggered: {
                                    model.enableFrametimeValue = !model.enableFrametimeValue;
                                    frametimeTab.enabled = model.enableFrametimeValue
                                    frametimeRange.enabled = model.enableFrametimeValue
                                }
                            }
                        }
                        Label {
                            Layout.leftMargin: 20
                            text: model.frametimeRangeName
                        }
                        SpinBox {
                            id: frametimeRange
                            from: 30
                            to: 180
                            stepSize: 10
                            editable: true
                            value: model.frametimeRangeValue
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            ToolTip.text: model.frametimeRangeTooltip
                            textFromValue: function(value, locale) { return value.toString() + ' frames'; }
                            valueFromText: function(value, locale) { return value.replace(' frames', ''); }
                            onValueChanged: {
                                if (model.frametimeRangeValue !== value) model.frametimeRangeValue = Utils.round(value, 0);;
                            }
                        }

                        Switch {
                            Layout.columnSpan: 3
                            text: model.enableDeltaRenderingName
                            checked: model.enableDeltaRenderingValue
                            ToolTip.delay: 500
                            ToolTip.visible: hovered
                            ToolTip.text: model.enableDeltaRenderingTooltip
                            action: Action {
                                onTriggered: {
                                    model.enableDeltaRenderingValue = !model.enableDeltaRenderingValue;
                                }
                            }
                        }

                        Button {
                            Layout.columnSpan: 3
                            text: "Revert to default settings"
                            action: Action {
                                onTriggered: {
                                    fpsTab.enabled  = true;
                                    tearTab.enabled = true;
                                    frametimeTab.enabled = true;
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
                                ToolTip.text: model.colorTooltip
                                ToolTip.delay: 500
                                ToolTip.visible: hovered
                            }
                            Rectangle {
                                id: fpsColorRectangle
                                height: 20
                                color: model.fpsOptionsEnabled ? model.color : "#8b8b8b"
                                border.color: "#8066b0"
                                border.width: 1
                                radius: 3
                                Layout.leftMargin:  50
                                Layout.rightMargin: 50
                                Layout.fillWidth: true
                                MouseArea {
                                    enabled: model.fpsOptionsEnabled
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
                                Layout.columnSpan: 2
                                text:  "Replicate Color"
                                //ToolTip.text: "Replicate this color to tears and frametime of this video index"
                                //ToolTip.delay: 500
                                //ToolTip.visible: hovered
                                enabled: model.fpsOptionsEnabled
                                action: Action {
                                    onTriggered:
                                        tearOptionsModel.applyColor(model.color, index)
                                }
                            }

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
                                to: 255
                                enabled: model.fpsOptionsEnabled
                                stepSize: 1
                                editable: true
                                value: model.pixelDifference
                                ToolTip.delay: 500
                                ToolTip.visible: hovered
                                ToolTip.text: model.pixelDifferenceTooltip
                                onValueChanged: {
                                    if (model.pixelDifference !== value) model.pixelDifference = value;
                                }
                            }
                            Button {
                                Layout.columnSpan: 2
                                text: "Apply to all videos"
                                enabled: model.fpsOptionsEnabled
                                action: Action {
                                    onTriggered: fpsOptionsModel.applyPixelDifference(model.pixelDifference)
                                }
                            }

                            Label {
                                text: model.displayedTextName
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
                                TextInput {
                                    id: fpsText
                                    anchors.fill: parent
                                    leftPadding: 5
                                    topPadding: 2
                                    bottomPadding: 2
                                    enabled: model.fpsOptionsEnabled
                                    text: model.displayedText
                                    color: enabled && model.fpsOptionsEnabled ? model.color
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
                                enabled: model.fpsOptionsEnabled
                                onClicked: {
                                    fontDialog.open()
                                }
                            }
                            FontDialog {
                                id: fontDialog
                                title: "Please choose a font"
                                font: Qt.font({ family: "Fjalla One", pointSize: 18 })
                                onAccepted: {
                                    fpsText.font = fontDialog.font
                                    model.displayedTextFont = fontDialog.font
                                }
                            }
                            Switch {
                                id: fpsTextEnabled
                                checked: true
                                enabled: model.fpsOptionsEnabled
                                action: Action {
                                    onTriggered: {
                                        fpsText.enabled = !fpsText.enabled;
                                        fpsTextCustomize.enabled = !fpsTextCustomize.enabled;
                                        fpsTextEnabled.checked = fpsText.enabled
                                        model.displayedTextEnabled = fpsText.enabled
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
                                id: colorLabel
                                text: model.colorName + ":"
                                Layout.rightMargin: 5
                            }
                            Rectangle {
                                id: tearColorRectangle
                                height: 20
                                color: model.tearOptionsEnabled ? model.color : "#8b8b8b"
                                border.color: "#8066b0"
                                border.width: 1
                                radius: 3
                                Layout.leftMargin:  50
                                Layout.rightMargin: 50
                                Layout.fillWidth: true
                                ToolTip.text: model.colorTooltip
                                MouseArea {
                                    anchors.fill: parent
                                    enabled: model.tearOptionsEnabled
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
                                text:  "Replicate Color"
                                enabled: model.tearOptionsEnabled
                                action: Action {
                                    onTriggered:
                                        fpsOptionsModel.applyColor(model.color, index)
                                }
                            }

                            Label {
                                text: model.pixelDifferenceName
                            }
                            SpinBox {
                                id: tearPercentage
                                from: 0
                                to: 100
                                stepSize: 1
                                editable: true
                                enabled: model.tearOptionsEnabled
                                value: model.pixelDifference
                                textFromValue: function(value, locale) { return value.toString() + '%'; }
                                valueFromText: function(value, locale) { return value.replace('%', ''); }
                                onValueChanged: {
                                    if (model.pixelDifference !== value){ model.pixelDifference = value; }
                                }
                            }
                            Button {
                                text: "Apply to all"
                                enabled: model.tearOptionsEnabled
                                action: Action {
                                    onTriggered: {
                                        tearOptionsModel.applyTearPercentage(model.pixelDifference)
                                    }
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
