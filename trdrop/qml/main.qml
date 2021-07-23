import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Controls 2.0
import QtQuick.Controls.Material 2.0
import QtQuick.Dialogs 1.2
import QtQuick.Controls.Styles 1.4

ApplicationWindow
{
    // startup as a windowed application
    id: rootWindow
    minimumWidth: 1280
    minimumHeight: 720
    visible: true
    // TODO refactor this so the user may choose a light theme
    Material.theme: Material.Dark
    Material.accent: Material.Purple

    //
    menuBar: TrdropMenubar { }
    // default content
    StartupBackground {
        id: startupBackground
        visible: true
        // disable the background if the export as overlay and the text would show
        Connections {
            target: fileItemModel
            function onDataChanged() { startupBackground.visible = videocapturelist.getOpenVideosCount() === 0; }
        }
    }
    // drawn over the startup background for simplicity
    TrdropContent {
        visible: true
    }
    // only allow fullscreen view
    //Component.onCompleted: {
    //    rootWindow.showFullScreen();
    //}

    // not needed yet
    // statusBar: TrdropStatusBar { }
}
