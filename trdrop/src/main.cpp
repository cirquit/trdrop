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
#include "headers/imageviewer.h"
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

    //! TODO
    qRegisterMetaType<cv::Mat>("cv::Mat");

    qmlRegisterType<QMLImageViewer>("Trdrop", 1, 0, "QMLImageViewer");

    //ImageViewer view;
    //QMLImageViewer view;
    Capture capture;
    Converter converter;
    CustomThread captureThread;
    CustomThread converterThread;
    // Everything runs at the same priority as the gui, so it won't supply useless frames.
    converter.setProcessAll(false);
    captureThread.start();
    converterThread.start();
    capture.moveToThread(&captureThread);
    //converter.moveToThread(&converterThread);
    QObject::connect(&capture, &Capture::frameReady, &converter, &Converter::processFrame);

    engine.rootContext()->setContextProperty("converter", &converter);
    //QObject::connect(&converter, &Converter::imageReady, &view, &QMLImageViewer::setImage);
    //view.show();
    // QObject::connect(&capture, &Capture::started, [](){ qDebug() << "Capture started."; });
    QMetaObject::invokeMethod(&capture, "start");

    // load application
    engine.load(QUrl(QStringLiteral("qrc:/qml/main.qml")));
    return app.exec();
}
