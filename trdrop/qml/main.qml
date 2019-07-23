import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Controls 2.0
import QtQuick.Controls.Material 2.0
import QtQuick.Dialogs 1.2
import QtQuick.Controls.Styles 1.4

ApplicationWindow
{
    // startup as a fullscreen application
    id: rootWindow
    minimumWidth: Screen.width
    minimumHeight: Screen.height
    visible: true
    // TODO refactor this so the user may choose a light theme
    Material.theme: Material.Dark
    Material.accent: Material.Purple

    //
    menuBar: TrdropMenubar { }
    // default content
    StartupBackground {
        visible: true
    }
    // drawn over the startup background for simplicity
    TrdropContent {
        visible: true
    }
    // not needed yet
    // statusBar: TrdropStatusBar { }
}
