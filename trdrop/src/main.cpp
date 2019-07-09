#include <QApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>
#include <QQuickView>
#include <QQmlContext>
#include <QFontDatabase>

#include "opencv2/core/core.hpp"
#include "opencv2/highgui/highgui.hpp"

#include "headers/qml_models/fileitemmodel.h"
#include "headers/qml_models/generaloptionsmodel.h"
#include "headers/qml_models/fpsoptionsmodel.h"
#include "headers/qml_models/tearoptionsmodel.h"
#include "headers/qml_models/resolutionsmodel.h"
#include "headers/qml_models/imageformatmodel.h"
#include "headers/qml_models/videoformatmodel.h"
#include "headers/qml_models/exportoptionsmodel.h"

#include "headers/qml_interface/videocapturelist_qml.h"
#include "headers/qml_interface/imageconverter_qml.h"
#include "headers/qml_interface/imagecomposer_qml.h"
#include "headers/qml_interface/framerateprocessing_qml.h"
#include "headers/qml_interface/deltaprocessing_qml.h"
#include "headers/qml_interface/renderer_qml.h"
#include "headers/qml_interface/viewer_qml.h"
#include "headers/qml_interface/exporter_qml.h"

#include "headers/cpp_interface/frameratemodel.h"

int main(int argc, char *argv[])
{
    // general application stuff
    QCoreApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    QApplication app(argc, argv);
    QQmlApplicationEngine engine;
    QQuickStyle::setStyle("Material");
    QFontDatabase::addApplicationFont("qrc:/fonts/materialdesignicons-webfont.ttf");

    // c++ models
    FramerateModel framerate_model;
    std::shared_ptr<FramerateModel> shared_framerate_model(&framerate_model);
    //
    QList<FPSOptions> fps_option_list;
    std::shared_ptr<QList<FPSOptions>> shared_fps_options_list(&fps_option_list);

    // qml models
    // prepare the FileItemModel
    qmlRegisterType<FileItemModel>();
    constexpr quint8 default_file_items_count = 3;
    FileItemModel file_item_model(default_file_items_count);
    engine.rootContext()->setContextProperty("fileItemModel", &file_item_model);

    // prepare the Tear Options Model
    qmlRegisterType<TearOptionsModel>();
    TearOptionsModel tear_options_model;
    engine.rootContext()->setContextProperty("tearOptionsModel", &tear_options_model);

    // prepare the FPS Options Model
    qmlRegisterType<FPSOptionsModel>();
    FPSOptionsModel fps_options_model(shared_framerate_model, shared_fps_options_list);
    engine.rootContext()->setContextProperty("fpsOptionsModel", &fps_options_model);

    // prepare the OptionsModel
    qmlRegisterType<GeneralOptionsModel>();
    GeneralOptionsModel general_options_model;
    engine.rootContext()->setContextProperty("generalOptionsModel", &general_options_model);
    std::shared_ptr<GeneralOptionsModel> shared_general_options_model(&general_options_model);

    // prepare ResolutionsModel (Exporter)
    qmlRegisterType<ResolutionsModel>();
    ResolutionsModel resolutions_model;
    engine.rootContext()->setContextProperty("resolutionsModel", &resolutions_model);
    std::shared_ptr<ResolutionsModel> shared_resolution_model(&resolutions_model);

    // prepare ImagFormatModel (Exporter)
    qmlRegisterType<ImageFormatModel>();
    ImageFormatModel imageformat_model;
    engine.rootContext()->setContextProperty("imageFormatModel", &imageformat_model);
    std::shared_ptr<ImageFormatModel> shared_imageformat_model(&imageformat_model);

    // prepare VideoFormatModel (Exporter)
    qmlRegisterType<VideoFormatModel>();
    VideoFormatModel videoformat_model;
    engine.rootContext()->setContextProperty("videoFormatModel", &videoformat_model);

    // prepare ExportOptionsModel (Exporter)
    qmlRegisterType<ExportOptionsModel>();
    ExportOptionsModel export_options_model;
    engine.rootContext()->setContextProperty("exportOptionsModel", &export_options_model);
    std::shared_ptr<ExportOptionsModel> shared_export_options_model(&export_options_model);

    // allow cv::Mat in signals
    qRegisterMetaType<cv::Mat>("cv::Mat");
    // allow const QList<FPSOptions> in signals
    qRegisterMetaType<QList<FPSOptions>>("const QList<FPSOptions>");
    // register the viewer as qml type
    qmlRegisterType<ViewerQML>("Trdrop", 1, 0, "ViewerQML");

    VideoCaptureListQML videocapturelist_qml(default_file_items_count);
    engine.rootContext()->setContextProperty("videocapturelist", &videocapturelist_qml);
    FramerateProcessingQML framerate_processing_qml(shared_framerate_model, shared_fps_options_list);
    engine.rootContext()->setContextProperty("framerateprocessing", &framerate_processing_qml);
    DeltaProcessingQML delta_processing_qml(shared_fps_options_list, shared_general_options_model);
    engine.rootContext()->setContextProperty("deltaprocessing", &delta_processing_qml);
    ImageConverterQML imageconverter_qml;
    engine.rootContext()->setContextProperty("imageconverter", &imageconverter_qml);
    ImageComposerQML imagecomposer_qml(shared_resolution_model);
    engine.rootContext()->setContextProperty("imagecomposer", &imagecomposer_qml);
    RendererQML renderer_qml(shared_fps_options_list);
    engine.rootContext()->setContextProperty("renderer", &renderer_qml);
    ExporterQML exporter_qml(shared_export_options_model
                           , shared_imageformat_model);
    engine.rootContext()->setContextProperty("exporter", &exporter_qml);

    // sigals in c++ (main processing pipeline)
    // pass the QList<cv::Mat> to the converter
    QObject::connect(&videocapturelist_qml, &VideoCaptureListQML::framesReady, &framerate_processing_qml, &FramerateProcessingQML::processFrames);
    // tearprocessing
    QObject::connect(&framerate_processing_qml, &FramerateProcessingQML::framesReady, &delta_processing_qml, &DeltaProcessingQML::processFrames);
    // frametime processing
    QObject::connect(&delta_processing_qml, &DeltaProcessingQML::framesReady, &imageconverter_qml, &ImageConverterQML::processFrames);
    // pass the QList<QImage> to the composer to mux them together
    QObject::connect(&imageconverter_qml,   &ImageConverterQML::imagesReady,   &imagecomposer_qml,    &ImageComposerQML::processImages);
    // pass the QImage to the renderer to render the meta information onto the image
    QObject::connect(&imagecomposer_qml,    &ImageComposerQML::imageReady,     &renderer_qml,         &RendererQML::processImage);
    // pass the rendered QImage to the exporter
    QObject::connect(&renderer_qml,         &RendererQML::imageReady,          &exporter_qml,         &ExporterQML::processImage);

    // if VCL finishes processing, finish exporting (may be needed if it's a video)
    QObject::connect(&videocapturelist_qml, &VideoCaptureListQML::finishedProcessing, &exporter_qml, &ExporterQML::finishExporting);

    // the exporter may trigger a request for new frames from VCL
    QObject::connect(&exporter_qml,         &ExporterQML::requestNextImages,   &videocapturelist_qml, &VideoCaptureListQML::readNextFrames);

    // meta data pipeline
    // link the fps options with the renderer
    QObject::connect(&fps_options_model, &FPSOptionsModel::dataChanged, &renderer_qml, &RendererQML::redraw);
    // TODO tear options
    // TODO frametime options
    // TODO tear values
    // TODO fps values
    // TODO frametime values
    // TODO general option values

    // load application
    engine.load(QUrl(QStringLiteral("qrc:/qml/main.qml")));
    return app.exec();
}
