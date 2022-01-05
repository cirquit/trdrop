#pragma once

#include <QtCore/qglobal.h>

#if defined(TRDROPLIB_LIBRARY)
#  define TRDROPLIB_EXPORT Q_DECL_EXPORT
#else
#  define TRDROPLIB_EXPORT Q_DECL_IMPORT
#endif
