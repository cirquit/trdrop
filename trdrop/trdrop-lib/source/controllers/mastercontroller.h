#pragma once

#include <QObject>
#include <QString>
#include <trdrop-lib_global.h>

namespace trdrop {
namespace controllers {

class TRDROPLIB_EXPORT MasterController : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString ui_welcomeMessage MEMBER welcomeMessage CONSTANT)
public:
    explicit MasterController(QObject* parent = nullptr);

public:
    QString welcomeMessage = "This is Mastercontroller to Major Tom";
};
}
}
