#include "opencv2/opencv.hpp"
#include <math.h>
#include <string>
#include <thread>
#include <chrono>


void printProgress(const int &currentIndex, const int &maxIndex) {

	double progress = static_cast<double>(currentIndex) / static_cast<double>(maxIndex);
	int width = 50;
	int chars = static_cast<int>(progress * width);
	int spaces = width - chars;

	std::cout << "Progress: ["
		<< std::string(chars, '#')
		<< std::string(spaces, ' ')
		<< "] "
		<< std::setprecision(4)
		<< progress*100.0
		<< "%\r"
		<< std::flush;
}

int main(int, char**)
{
	int plotWindow = 186;
	std::deque<double> video1Fps(plotWindow, 0);
	std::deque<double> video2Fps(plotWindow, 0);

	std::vector<std::deque<double>> fpsValues{ video1Fps, video2Fps };
	std::vector<cv::Scalar> plotColors{ cv::Scalar(204, 171, 66), cv::Scalar(70, 93, 255) };

	while (count > 0)
	{

		cv::Mat display;

		double maxFrames = cap.get(CV_CAP_PROP_FRAME_COUNT);

		int cornerDistance = 30;

		cv::Size frameSize(display.size());
		cv::Scalar graphColor(255, 255, 255);

		double pointGap = maxFrames / (60 * frameSize.width);

		int height = frameSize.height / 4;
		int width = frameSize.width - 2 * cornerDistance;

		int x = cornerDistance;
		int y = frameSize.height - cornerDistance - height;

		cv::Mat roi = display(cv::Rect(x, y, width, height));
		cv::Mat color(roi.size(), CV_8UC3, graphColor);
		double alpha = 0.4;
		cv::addWeighted(color, alpha, roi, 1.0 - alpha, 0.0, roi);


		//y-line
		cv::line(display, cv::Point(x, y), cv::Point(x, y + height), graphColor, 3, 10);
		cv::putText(display, "FPS", cv::Point(x - 16, y - 9), CV_FONT_HERSHEY_DUPLEX, 0.5, cv::Scalar(0, 0, 0));
		cv::putText(display, "FPS", cv::Point(x - 15, y - 10), CV_FONT_HERSHEY_DUPLEX, 0.5, graphColor);
		//x-line
		cv::line(display, cv::Point(x, y + height), cv::Point(x + width, y + height), graphColor, 3, 10);

		for (int i = 1; i < 6; ++i) {
			int lineY = (60 - 10 * i*height / 60) + frameSize.height - 60 - cornerDistance;
			cv::line(display, cv::Point(x, lineY), cv::Point(x + width, lineY), graphColor);
			cv::putText(display, std::to_string(i * 10), cv::Point(x - 28, lineY + 5), CV_FONT_HERSHEY_DUPLEX, 0.5, cv::Scalar(0, 0, 0));
			cv::putText(display, std::to_string(i * 10), cv::Point(x - 27, lineY + 6), CV_FONT_HERSHEY_DUPLEX, 0.5, graphColor);
		}

		int pointDistance = cornerDistance;
		int pointDistanceIncrement = width / plotWindow;

		cv::Point lastPoint(cornerDistance + 6, frameSize.height - cornerDistance - 4);
		std::vector<cv::Point> lastPoints(fpsValues.size(), lastPoint);

		for (int i = 0; i < fpsValues[0].size(); ++i) {
			for (int vix = 0; vix < fpsValues.size(); ++vix) {
				int currentFps = static_cast<int>(fpsValues[vix][i]);
				int y = (60 - currentFps*height / 60) + frameSize.height - 60 - cornerDistance - 4;
				cv::Point currentPoint(pointDistance + 6, y);
				cv::line(display, lastPoints[vix], currentPoint, plotColors[vix], 2, CV_AA);
				lastPoints[vix] = currentPoint;
			}
			pointDistance += pointDistanceIncrement;
		}
	}

}
