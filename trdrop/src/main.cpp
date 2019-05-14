#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>
#include <QQuickView>
#include <QQmlContext>
#include <QFontDatabase>

#include "headers/fileitemmodel.h"

int main(int argc, char *argv[])
{
    // general application stuff
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication app(argc, argv);
    QQmlApplicationEngine engine;
    QQuickStyle::setStyle("Material");
    QFontDatabase::addApplicationFont("qrc:/fonts/materialdesignicons-webfont.ttf");
    // prepare the FileItemModel
    qmlRegisterType<FileItemModel>();
    constexpr quint8 default_file_items = 3;
    FileItemModel file_item_model(default_file_items);
    engine.rootContext()->setContextProperty("fileItemModel", &file_item_model);
    // prepare the OptionsModel

    // load application
    engine.load(QUrl(QStringLiteral("qrc:/qml/main.qml")));
    return app.exec();
}
