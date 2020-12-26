#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>
#include <QQuickView>
#include <QQmlContext>
#include <QFontDatabase>
//#include <QQmlDebuggingEnabler>

#include "opencv2/core/core.hpp"
#include "opencv2/highgui/highgui.hpp"

#include "headers/qml_models/fileitemmodel.h"
#include "headers/qml_models/generaloptionsmodel.h"
#include "headers/qml_models/framerateoptionsmodel.h"
#include "headers/qml_models/tearoptionsmodel.h"
#include "headers/qml_models/resolutionsmodel.h"
#include "headers/qml_models/imageformatmodel.h"
#include "headers/qml_models/exportoptionsmodel.h"

#include "headers/qml_interface/videocapturelist_qml.h"
#include "headers/qml_interface/imageconverter_qml.h"
#include "headers/qml_interface/imagecomposer_qml.h"
#include "headers/qml_interface/frameprocessing_qml.h"
#include "headers/qml_interface/renderer_qml.h"
#include "headers/qml_interface/viewer_qml.h"
#include "headers/qml_interface/exporter_qml.h"

#include "headers/cpp_interface/frameratemodel.h"
#include "headers/cpp_interface/frametimemodel.h"
#include "headers/cpp_interface/framerateplot.h"
#include "headers/cpp_interface/frametimeplot.h"

int main(int argc, char *argv[])
{
    // general application stuff
    //QQmlDebuggingEnabler enabler;
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication app(argc, argv);
    QQmlApplicationEngine engine;
    app.setOrganizationName("trdrop");
    app.setOrganizationDomain("trdrop");
    QQuickStyle::setStyle("Material");
    QFontDatabase::addApplicationFont(":/fonts/FjallaOne-Regular.ttf");
    // TODO evaluate if we need these fonts
    QFontDatabase::addApplicationFont(":/fonts/materialdesignicons-webfont.ttf");
    QFontDatabase::addApplicationFont(":/fonts/Rationale-Regular.ttf");

    // c++ models
    std::shared_ptr<FramerateModel> shared_framerate_model(new FramerateModel());
    std::shared_ptr<FrametimeModel> shared_frametime_model(new FrametimeModel());
    std::shared_ptr<QList<FramerateOptions>> shared_fps_options_list(new QList<FramerateOptions>());
    std::shared_ptr<QList<TearOptions>> shared_tear_options_list(new QList<TearOptions>());

    // qml models
    // prepare the FileItemModel
    qmlRegisterType<FileItemModel>();
    constexpr quint8 default_file_items_count = 3;
    FileItemModel file_item_model(default_file_items_count);
    engine.rootContext()->setContextProperty("fileItemModel", &file_item_model);

    // prepare the Tear Options Model
    qmlRegisterType<TearOptionsModel>();
    TearOptionsModel tear_options_model(shared_tear_options_list);
    engine.rootContext()->setContextProperty("tearOptionsModel", &tear_options_model);

    // prepare the OptionsModel
    qmlRegisterType<GeneralOptionsModel>();
    std::shared_ptr<GeneralOptionsModel> shared_general_options_model(new GeneralOptionsModel());
    engine.rootContext()->setContextProperty("generalOptionsModel", &(*shared_general_options_model));

    // prepare ResolutionsModel (Exporter)
    qmlRegisterType<ResolutionsModel>();
    std::shared_ptr<ResolutionsModel> shared_resolution_model(new ResolutionsModel());
    engine.rootContext()->setContextProperty("resolutionsModel", &(*shared_resolution_model));

    // prepare the FPS Options Model
    qmlRegisterType<FramerateOptionsModel>();
    FramerateOptionsModel framerate_options_model(shared_framerate_model, shared_fps_options_list, shared_resolution_model);
    engine.rootContext()->setContextProperty("framerateOptionsModel", &framerate_options_model);

    // prepare ImagFormatModel (Exporter)
    qmlRegisterType<ImageFormatModel>();
    std::shared_ptr<ImageFormatModel> shared_imageformat_model(new ImageFormatModel());
    engine.rootContext()->setContextProperty("imageFormatModel", &(*shared_imageformat_model));

    // prepare ExportOptionsModel (Exporter)
    qmlRegisterType<ExportOptionsModel>();
    //ExportOptionsModel export_options_model;
    std::shared_ptr<ExportOptionsModel> shared_export_options_model(new ExportOptionsModel());
    engine.rootContext()->setContextProperty("exportOptionsModel", &(*shared_export_options_model));

    // allow cv::Mat in signals
    qRegisterMetaType<cv::Mat>("cv::Mat");
    // allow const QList<FPSOptions> in signals
    qRegisterMetaType<QList<FramerateOptions>>("const QList<FPSOptions>");
    // allow const QList<quint8> in signals
    qRegisterMetaType<QList<quint8>>("const QList<quint8>");

    // register the viewer as qml type
    qmlRegisterType<ViewerQML>("Trdrop", 1, 0, "ViewerQML");

    // c++ plots
    std::shared_ptr<FrameratePlot> shared_framerate_plot_instance(new FrameratePlot(shared_framerate_model
                                                      , shared_fps_options_list
                                                      , shared_resolution_model
                                                      , shared_general_options_model));
    std::shared_ptr<FrametimePlot> shared_frametime_plot_instance(new FrametimePlot(shared_frametime_model
                                                      , shared_fps_options_list
                                                      , shared_resolution_model
                                                      , shared_general_options_model));
    std::shared_ptr<TearModel> shared_tear_model(new TearModel(shared_tear_options_list
                                                             , shared_resolution_model
                                                             , shared_general_options_model));
    // qml objects
    VideoCaptureListQML videocapturelist_qml(default_file_items_count);
    engine.rootContext()->setContextProperty("videocapturelist", &videocapturelist_qml);
    FrameProcessingQML frame_processing_qml(shared_framerate_model
                                          , shared_frametime_model
                                          , shared_fps_options_list
                                          , shared_tear_options_list
                                          , shared_general_options_model
                                          , shared_tear_model);
    engine.rootContext()->setContextProperty("frameprocessing", &frame_processing_qml);
    ImageConverterQML imageconverter_qml;
    engine.rootContext()->setContextProperty("imageconverter", &imageconverter_qml);
    ImageComposerQML imagecomposer_qml(shared_resolution_model);
    engine.rootContext()->setContextProperty("imagecomposer", &imagecomposer_qml);
    RendererQML renderer_qml(shared_fps_options_list
                           , shared_general_options_model
                           , shared_export_options_model
                           , shared_framerate_plot_instance
                           , shared_frametime_plot_instance
                           , shared_tear_model
                           , shared_resolution_model);
    engine.rootContext()->setContextProperty("renderer", &renderer_qml);
    ExporterQML exporter_qml(shared_export_options_model
                           , shared_imageformat_model
                           , shared_framerate_model);
    engine.rootContext()->setContextProperty("exporter", &exporter_qml);

    // sigals in c++ (main processing pipeline)
    // pass the QList<cv::Mat> to the converter
    QObject::connect(&videocapturelist_qml, &VideoCaptureListQML::framesReady, &frame_processing_qml, &FrameProcessingQML::processFrames, Qt::DirectConnection);
    // framerate processing
    QObject::connect(&frame_processing_qml, &FrameProcessingQML::framesReady,  &imageconverter_qml,   &ImageConverterQML::processFrames, Qt::DirectConnection);
    // pass the QList<QImage> to the composer to mux them together
    QObject::connect(&imageconverter_qml,   &ImageConverterQML::imagesReady,   &imagecomposer_qml,    &ImageComposerQML::processImages, Qt::DirectConnection);
    // pass the QImage to the renderer to render the meta information onto the image
    QObject::connect(&imagecomposer_qml,    &ImageComposerQML::imageReady,     &renderer_qml,         &RendererQML::processImage, Qt::DirectConnection);
    // pass the rendered QImage to the exporter
    QObject::connect(&renderer_qml,         &RendererQML::imageReady,          &exporter_qml,         &ExporterQML::processImage, Qt::DirectConnection);

    // if VCL finishes processing, finish exporting (close io-handles if need be)
    QObject::connect(&videocapturelist_qml, &VideoCaptureListQML::finishedProcessing, &exporter_qml, &ExporterQML::finishExporting);

    // the exporter may trigger a request for new frames from VCL
    QObject::connect(&exporter_qml,         &ExporterQML::requestNextImages,   &videocapturelist_qml, &VideoCaptureListQML::readNextFrames);

    // meta data pipeline
    // link the options with the renderer
    QObject::connect(&framerate_options_model,         &FramerateOptionsModel::dataChanged, &renderer_qml, &RendererQML::redraw);
    QObject::connect(&tear_options_model,              &TearOptionsModel::dataChanged,      &renderer_qml, &RendererQML::redraw);
    QObject::connect(&(*shared_general_options_model), &GeneralOptionsModel::dataChanged,   &renderer_qml, &RendererQML::redraw);

    // load application
    engine.load(QUrl(QStringLiteral("qrc:/qml/main.qml")));
    return app.exec();
}
