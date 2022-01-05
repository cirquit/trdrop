#include "tests.h"
#include "ui_tests.h"

Tests::Tests(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::Tests)
{
    ui->setupUi(this);
}

Tests::~Tests()
{
    delete ui;
}

