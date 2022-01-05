#include "tests.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Tests w;
    w.show();
    return a.exec();
}
