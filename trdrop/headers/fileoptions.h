#ifndef FILEOPTIONS_H
#define FILEOPTIONS_H

#include "headers/checkboxitem.h"

class FileOptions
{
// constructors
public:
    //! TODO
    FileOptions(quint8 & video_id)
        : video_id(video_id)
    {
        _init_member();
    }

// methods
private:
    //! TODO
    void _init_member()
    {
        option_01.setName("option 01");
        option_01.setTooltip("By default true");
        option_01.setValue(true);

        option_02.setName("option 02");
        option_02.setTooltip("By default false");
        option_02.setValue(false);

        option_03.setName("option 03");
        option_03.setTooltip("By default true");
        option_03.setValue(true);
    }

// member
public:
    //! TODO
    quint8       video_id;
    //! TODO
    CheckBoxItem option_01;
    CheckBoxItem option_02;
    CheckBoxItem option_03;
};

#endif // FILEOPTIONS_H
