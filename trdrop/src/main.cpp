#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>
#include <QQuickView>
#include <QQmlContext>
#include <QFontDatabase>

#include "opencv2/core/core.hpp"
#include "opencv2/highgui/highgui.hpp"

#include "headers/fileitemmodel.h"
#include "headers/generaloptionsmodel.h"
#include "headers/fpsoptionsmodel.h"
#include "headers/tearoptionsmodel.h"

#include "headers/capture.h"
#include "headers/converter.h"
#include "headers/qml_imageviewer.h"
#include "headers/customthread.h"

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

    // prepare the Tear Options Model
    qmlRegisterType<TearOptionsModel>();
    TearOptionsModel tear_options_model;
    engine.rootContext()->setContextProperty("tearOptionsModel", &tear_options_model);

    // prepare the FPS Options Model
    qmlRegisterType<FPSOptionsModel>();
    FPSOptionsModel fps_options_model;
    engine.rootContext()->setContextProperty("fpsOptionsModel", &fps_options_model);

    // prepare the OptionsModel
    qmlRegisterType<GeneralOptionsModel>();
    GeneralOptionsModel general_options_model;
    engine.rootContext()->setContextProperty("generalOptionsModel", &general_options_model);

    //! allow cv::Mat in signals
    qRegisterMetaType<cv::Mat>("cv::Mat");

    qmlRegisterType<QMLImageViewer>("Trdrop", 1, 0, "QMLImageViewer");

    Capture capture;
    Converter converter;
    CustomThread captureThread;
    captureThread.start();
    capture.moveToThread(&captureThread);
    QObject::connect(&capture, &Capture::frameReady, &converter, &Converter::processFrame);

    engine.rootContext()->setContextProperty("capture", &capture);
    engine.rootContext()->setContextProperty("converter", &converter);
    QMetaObject::invokeMethod(&capture, "getNextFrame");

    // load application
    engine.load(QUrl(QStringLiteral("qrc:/qml/main.qml")));
    return app.exec();
}
