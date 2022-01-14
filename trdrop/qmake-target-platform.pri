win32 {
    CONFIG += PLATFORM_WIN
    # counts as MINGW
    win32-g++ {
        CONFIG += COMPILER_GCC
    }
    # not used for now
    win32-msvc2017 {
        CONFIG += COMPILER_MSVC2017
        win32-msvc2017:QMAKE_TARGET.arch = x86_64
    }
}

linux {
    CONFIG += PLATFORM_LINUX
    !contains(QT_ARCH, x86_64) {
        QMAKE_TARGET.arch = x86
    } else {
        QMAKE_TARGET.arch = x86_64
    }
    linux-g++ {
        CONFIG += COMPILER_GCC
    }
}

# not used for now
macx {
    CONFIG += PLATFORM_OSX
    macx-clang {
        CONFIG += COMPILER_CLANG
        QMAKE_TARGET.arch = x86_64
    }
    macx-clang-32{
        CONFIG += COMPILER_CLANG
        QMAKE_TARGET.arch = x86
    }
}

contains(QMAKE_TARGET.arch, x86_64) {
    CONFIG += PROCESSOR_x64
} else {
    CONFIG += PROCESSOR_x86
}

CONFIG(debug, release|debug) {
    CONFIG += BUILD_DEBUG
} else {
    CONFIG += BUILD_RELEASE
}
