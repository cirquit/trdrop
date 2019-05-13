#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>
#include <QQuickView>
#include <QQmlContext>
#include <QFontDatabase>

#include "headers/fileitemmodel.h"

int main(int argc, char *argv[])
{
    //
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication app(argc, argv);
    QQuickStyle::setStyle("Material");
    QFontDatabase::addApplicationFont("qrc:/fonts/materialdesignicons-webfont.ttf");
    //
    qmlRegisterType<FileItemModel>();
    FileItemModel file_item_model;
    //
    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("fileItemModel", &file_item_model);
    engine.load(QUrl(QStringLiteral("qrc:/qml/main.qml")));
    if (engine.rootObjects().isEmpty())
        return -1;

    return app.exec();
}
