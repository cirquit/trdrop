#include <iostream>
#include <string>
#include <algorithm>

#include<opencv2/core/core.hpp>
#include<opencv2/highgui/highgui.hpp>
#include<opencv2/imgproc/imgproc.hpp>

/*
 * Implicity increments the CV_CAP_PROP_POS_FRAMES by 1
 */
cv::Mat & getNextFrame(cv::VideoCapture & video) {
	cv::Mat frame;
	bool success = video.read(frame);
	std::cout << "success?: " << success << '\n';
	return success ? frame : cv::Mat();
}

double getCurrentFrameIndex(cv::VideoCapture & video) {
	return video.get(CV_CAP_PROP_POS_FRAMES);
}

double getWidth(cv::VideoCapture & video) {
	return video.get(CV_CAP_PROP_FRAME_WIDTH);
}

double getHeight(cv::VideoCapture & video) {
	return video.get(CV_CAP_PROP_FRAME_HEIGHT);
}

double getFrameCount(cv::VideoCapture & video) {
	return video.get(CV_CAP_PROP_FRAME_COUNT);
}

size_t getPixelCount(cv::VideoCapture & video) {
	return static_cast<size_t>(getWidth(video) * getHeight(video));
}

double getFrameRate(cv::VideoCapture & video) {
	return video.get(CV_CAP_PROP_FPS);
}

double getVideoLength(cv::VideoCapture & video) {
	double frameRate(getFrameRate(video));
	if (frameRate > 0) {
		return getFrameCount(video) / frameRate;
	}
	else { // framerate leq zero
		return 0;
	}
	
}
/*
int countDifference(cv::Mat & frameA, cv::Mat & frameB) {
	int diffCount(0);
	for (int i = 0; i < frameA.row; ++i) {
		for (int j = 0; j < frameA.cols; ++j) {
			std::cout << "P1: " << frameA.at<cv::Vec3b>(i,j) << '\n';
			std::cout << "P2: " << frameB.at<cv::Vec3b>(i,j) << '\n';
			diffCount += frameA.at<cv::Vec3b>(i,j) == frameB.at<cv::Vec3b>(i,j) ? 1 : 0;
		}
	}
	return diffCount;
}*/

int main(int argc, char *argv) {
	
	std::string exampleVideo("test-video-01.avi");

	cv::VideoCapture video(exampleVideo);

	double fixedFPS(getFrameRate(video));

	std::cout << "Fixed Fps: " << fixedFPS << '\n';
	std::cout << "Fixed Framecount: " << getFrameCount(video) << '\n';
	std::cout << "Videolength in seconds: " << getVideoLength(video) << '\n';
	std::cout << "Current Frameindex: " << getCurrentFrameIndex(video) << '\n';
	cv::Mat frame1(getNextFrame(video));
	cv::Mat frame2(getNextFrame(video));
	std::cout << "p1: " << frame2.at<uchar>(1) << '\n';
	/*

	std::cout << "Current Frameindex: " << getCurrentFrameIndex(video) << '\n';
	cv::Mat frame2(getNextFrame(video));
	std::cout << "Current Frameindex: " << getCurrentFrameIndex(video) << '\n';
	std::cout << "Difference: " << countDifference(frame1, frame2) << '\n';
	//std::cout << "Fixed Framerate: " << fixedFPS << '\n';
	*/
	return 0;
} 