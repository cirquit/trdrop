#pragma once

#include <QMainWindow>

QT_BEGIN_NAMESPACE
namespace Ui { class Tests; }
QT_END_NAMESPACE

class Tests : public QMainWindow
{
    Q_OBJECT

public:
    Tests(QWidget *parent = nullptr);
    ~Tests();

private:
    Ui::Tests *ui;
};
