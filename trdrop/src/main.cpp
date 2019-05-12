#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>
#include <QQuickView>
#include <QQmlContext>
#include <QFontDatabase>

#include "headers/fileitemlist.h"

int main(int argc, char *argv[])
{
    //
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication app(argc, argv);
    QQuickStyle::setStyle("Material");
    QFontDatabase::addApplicationFont("qrc:/fonts/materialdesignicons-webfont.ttf");
    //
    qmlRegisterType<FileItem>();
    //
    FileItemList file_item_list;
    //
    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("fileItemList", &file_item_list);
    engine.load(QUrl(QStringLiteral("qrc:/qml/main.qml")));
    if (engine.rootObjects().isEmpty())
        return -1;

    return app.exec();
}
