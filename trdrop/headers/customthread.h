#ifndef CUSTOM_THREAD_H
#define CUSTOM_THREAD_H

#include <QThread>

class CustomThread final : public QThread { public: ~CustomThread() { quit(); wait(); } };

#endif // CUSTOM_THREAD_H
