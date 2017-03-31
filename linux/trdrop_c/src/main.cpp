#include <trdrop.hpp>

#include <algorithm> // for_each
#include <locale>
#include <string>
#include <tuple>
#include <utility> // pair
#include <vector>

#include <AvTranscoder/file/InputFile.hpp>
#include <AvTranscoder/progress/ConsoleProgress.hpp>
#include <AvTranscoder/properties/PixelProperties.hpp>
#include <AvTranscoder/properties/VideoProperties.hpp>
#include <AvTranscoder/reader/VideoReader.hpp>
#include <AvTranscoder/util.hpp> // PropertyVector

#define DEBUG_FILENAME "/home/rewrite/Videos/Sample 1 1080p FPS Drop Zelda Wii U.avi"
// #define DEBUG_FILENAME "/home/rewrite/Videos/Sample 2 1080p FPS Stable Skyrim XB1.avi"
// #define DEBUG_FILENAME "/home/rewrite/Videos/Sample 3 1080p Tearing Watch Dogs 2 PS4.avi"
// #define DEBUG_FILENAME "../../videos/Dirty Art Club - Rosslyn's Crypt.mp4"
// #define DEBUG_FILENAME "../../videos/test-video-01.avi"

int same_until(std::vector<char> a, std::vector<char> b)
{
    int diff = 0;
    for (int i = 0; i < a.size(); ++i) {
        diff += a[i] == b[i] ? 0 : 1;
    }
    return diff;
}

std::vector<std::tuple<int, int, int> > to_rgb_vector(const char* data, size_t width, int height)
{
    std::vector<std::tuple<int, int, int> > rgb_vector;

    for (int i = 0; i < height * width; i += 3) {
        int r = static_cast<int>(data[i]);
        int g = static_cast<int>(data[i + 1]);
        int b = static_cast<int>(data[i + 2]);

        if (r < 0)
            r = 256 + r;

        if (g < 0)
            g = 256 + g;

        if (b < 0)
            b = 256 + b;

        rgb_vector.push_back(std::make_tuple(r, g, b));
    }

    return rgb_vector;
}

int main(int argc, char** argv)
{
    avtranscoder::preloadCodecsAndFormats(); // load ffmpeg context

    avtranscoder::InputFile videoFile(DEBUG_FILENAME);

    const std::vector<float> fpss(trdrop::get_fps_from_properties(videoFile));
    for_each(fpss.begin(), fpss.end(),
        [](const float& fps) {
            std::cout << "Properties FPS: " << fps << '\n';
        });

    avtranscoder::VideoReader reader(avtranscoder::InputStreamDesc(DEBUG_FILENAME, 0));

    int fst = 0;
    int snd = 1;

    const char* fst_frame = (const char*)reader.readFrameAt(fst)->getData()[0];
    /*
    std::vector<char> fst_frame_vector = std::vector<char>(reader.readFrameAt(fst)->getDataSize());

    for (int i = 0; i < fst_frame_vector.size(); ++i) {
        fst_frame_vector[i] = fst_frame[i];
    }

    const char* snd_frame = (const char*)reader.readFrameAt(snd)->getData()[0];

    std::vector<char> snd_frame_vector = std::vector<char>(reader.readFrameAt(snd)->getDataSize());

    for (int i = 0; i < snd_frame_vector.size(); ++i) {
        snd_frame_vector[i] = snd_frame[i];
    }

    std::cout << fst_frame_vector[320] << '\n';
    std::cout << snd_frame_vector[320] << '\n';

    int diff = same_until(fst_frame_vector, snd_frame_vector);

    std::cout << "diff : " << diff << '\n';

    std::cout << reader.readFrameAt(snd)->getAVFrame().format << '\n';
    */

    int size = reader.readFrameAt(fst)->getDataSize();
    int width = *reader.readFrameAt(fst)->getLineSize();
    int height = size / width;

    std::vector<std::tuple<int, int, int> > rgb_vector(to_rgb_vector(fst_frame, height, width));

    std::cout << "size: " << size << '\n';
    std::cout << "width: " << width << '\n';
    std::cout << "height: " << height << '\n';

    std::cout << rgb_vector.size() << '\n';
    //char c = '{';
    //std::cout << "convert: " << static_cast<int>(c) << '\n';

    for (int px = 0; px < size / 3; ++px) {
        std::cout << "r: " << std::get<0>(rgb_vector[px])
                  << ", g: " << std::get<1>(rgb_vector[px])
                  << ", b: " << std::get<2>(rgb_vector[px]) << '\n';
    }
    //    for (int i = 0; i < fst_frame)

    /*
    const char* b2 = (const char*)reader.readFrameAt(snd)->getData()[0];
    char b2_val = b2[202];

    std::cout << b1_val << '\n';
    std::cout << b2_val << '\n';
    */
    //     char* result = malloc(reader.getOutputHeight() * reader.getOutputWidth() * sizeof(char));
    /*
    bool b = true;

    for (int i = 0; i < reader.getOutputHeight() * reader.getOutputWidth(); ++i) {

        //if (b1[i] != b2[i]) {
        //b &= false;
        // std::wcout << b1[i]; // << " - " << b2[i];
        //}
    }
*/

    /*
    avtranscoder::FileProperties file_prop(videoFile.getProperties());
    const std::vector<avtranscoder::VideoProperties> video_props(file_prop.getVideoProperties());
    const avtranscoder::VideoProperties video_prop(video_props[0]);
    const avtranscoder::PixelProperties pixel_prop(video_prop.getPixelProperties());
    avtranscoder::PropertyVector prop_vector(pixel_prop.asVector());
*/
    //  trdrop::print_properties(prop_vector);

    // avtranscoder::VideoProperties video_prop(videoFile.getProperties().getVideoProperties());

    /*
    // call to analyse to access getProperties()
    videoFile.analyse(p, avtranscoder::eAnalyseLevelFull);

    avtranscoder::PropertyVector properties(videoFile.getProperties().asVector());

    for_each(properties.begin(), properties.end(),
        [](std::pair<std::string, std::string> pair) {
            std::cout << std::get<0>(pair) << ": " << std::get<1>(pair) << '\n';
        });

    const std::vector<avtranscoder::VideoProperties>& videoPropVector = videoFile.getProperties().getVideoProperties();

    for_each(videoPropVector.begin(), videoPropVector.end(),
        [](const avtranscoder::VideoProperties& vprop) {
            std::cout << vprop.getFps() << '\n';
        });
    //    std::cout << videoFile.getProperties().getVideoProperties() << '\n';
    */
    return 0;
}